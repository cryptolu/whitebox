#!/usr/bin/env pypy
#-*- coding:utf-8 -*-

'''
Building circuit for AES 10 rounds
:: CIRCUIT WALK START
:: ORDERING START 31783 NODES
:: CODE SIZE 63343 OPERATIONS
:: MASKING START 63343 EVENTS
Used 409664 random bits
Generating final code
:: CIRCUIT WALK START
:: ORDERING START 2588871 NODES
:: CODE SIZE 5177486 OPERATIONS
Max bits state 926
Memory usage: 2^10 = 1024 bytes
Opcode data size: 16.47 MB
Num opcodes: 2588743 num random: 409664

real    0m16.585s
user    0m15.451s
sys     0m1.117s
Encrypting...

real    0m0.185s
user    0m0.177s
sys     0m0.008s

Ciphertext:
00000000: 47e8 c363 429a 5f3a dec2 12ed 3b38 2157  G..cB._:....;8!W
00000010: 29cc c6d3 dc02 fd64 1244 e00b 2d53 1a86  )......d.D..-S..
00000020: 9a62 043a c28d 2f79 0091 1395 9458 0d13  .b.:../y.....X..
00000030: a65f e8ef b243 4c67 fe8c 0864 851e e622  ._...CLg...d..."
00000040: b356 1bf9 6f9c 0fd9 7217 8305 e4a5 ca77  .V..o...r......w
00000050: cec6 074e 7bb9 e27d 2699 a8fd 8798 9f0a  ...N{..}&.......
00000060: 6eed 52fc 79ec 82cb e0eb c5a1 1789 4a2d  n.R.y.........J-
00000070: c608 e021 222b a499 613a cb46 d934 bb33  ...!"+..a:.F.4.3

Difference:
---

'''

import sys, os

from struct import pack

from libwb.bit import VarVec, Bit, OP
from libwb.gates.bitaes import AES
from libwb.orderer import Orderer

NR = 10
NLINMASK = 2 # 1 - no linear masking, 2 - first-order

KEY = open("key").read()[:16]
DISABLE_NONLINEAR_MASKING = bool(int(os.environ.get("DISABLE_NONLINEAR_MASKING", 0)))

try:
    os.unlink("build/code.c")
except OSError:
    pass

randused = 0

def randbit():
    global randused
    randused += 1
    return Bit(OP.RANDOM)

def LIN_initial_share(bit):
    res = bit
    shares = []
    for i in xrange(NLINMASK - 1):
        shares.append(randbit())
        res ^= shares[-1]
    shares.append(res)
    return tuple(shares)

def LIN_and(xs, ys):
    if NLINMASK == 1:
        return (xs[0] & ys[0], )
    elif NLINMASK == 2:
        res = r = randbit()
        for x in xs:
            for y in ys:
                res ^= x & y
        return (res, r)
    else:
        raise NotImplementedError("higher-order linear masking is not implemented")

def LIN_xor(xs, ys):
    return tuple(x ^ y for x, y in zip(xs, ys))

def LIN_not(xs):
    xs = list(xs)
    xs[0] ^= Bit.ONE
    return tuple(xs)

def LIN_decode(xs):
    res = xs[0]
    for x in xs[1:]:
        res ^= x
    return res

def LIN_randbit():
    return [randbit()] + [Bit.ZERO for _ in xrange(NLINMASK-1)]

def MINQ_initial_share(bit):
    a = LIN_initial_share(randbit())
    b = LIN_initial_share(randbit())
    c = LIN_xor(LIN_initial_share(bit), LIN_and(a, b))
    return (a, b, c)

def MINQ_refresh(xs, rs):
    a, b, c = xs
    ra, rb, rc = rs
    ma = LIN_and(ra, LIN_xor(b, rc))
    mb = LIN_and(rb, LIN_xor(a, rc))
    rmul = LIN_and(LIN_xor(ra, rc), LIN_xor(rb, rc))
    rc = LIN_xor(rc, LIN_xor(ma, LIN_xor(mb, rmul)))
    a = LIN_xor(a, ra)
    b = LIN_xor(b, rb)
    c = LIN_xor(c, rc)
    return a, b, c

def MINQ_xor(xs, ys):
    rxs = ra, rb, rc = LIN_randbit(), LIN_randbit(), LIN_randbit()
    rys = rd, re, rf = LIN_randbit(), LIN_randbit(), LIN_randbit()
    a, b, c = MINQ_refresh(xs, rxs)
    d, e, f = MINQ_refresh(ys, rys)
    x = LIN_xor(a, d)
    y = LIN_xor(b, e)
    ae = LIN_and(a, e)
    bd = LIN_and(b, d)
    z = LIN_xor(c, LIN_xor(f, LIN_xor(ae, bd)))
    return x, y, z

def MINQ_and(xs, ys):
    rxs = ra, rb, rc = LIN_randbit(), LIN_randbit(), LIN_randbit()
    rys = rd, re, rf = LIN_randbit(), LIN_randbit(), LIN_randbit()
    a, b, c = MINQ_refresh(xs, rxs)
    d, e, f = MINQ_refresh(ys, rys)
    ma = LIN_xor(LIN_and(b, f), LIN_and(rc, e))
    md = LIN_xor(LIN_and(c, e), LIN_and(rf, b))
    x = LIN_xor(rf, LIN_and(a, e))
    y = LIN_xor(rc, LIN_and(b, d))
    ama = LIN_and(a, ma)
    dmd = LIN_and(d, md)
    rcrf = LIN_and(rc, rf)
    cf = LIN_and(c, f)
    z = LIN_xor(ama, LIN_xor(dmd, LIN_xor(rcrf, cf)))
    return x, y, z

def MINQ_not(xs):
    xs = list(xs)
    xs[2] = LIN_not(xs[2])
    return tuple(xs)

def MINQ_decode(xs):
    res = LIN_xor(xs[2], LIN_and(xs[0], xs[1]))
    return LIN_decode(res)

xbits = VarVec("x", 128)


# build reference AES circuit
KEY_BINARY = "".join(bin(ord(c))[2:].zfill(8) for c in KEY)
kbits = [(Bit.ZERO, Bit.ONE)[int(b)] for b in KEY_BINARY]

print "Building circuit for %d rounds of AES" % NR
ybits, k10 = AES(xbits, kbits, nr=NR)
co = Orderer(xbits=xbits, ybits=ybits).compile()

print "Masking", len(co.code), "events"
if DISABLE_NONLINEAR_MASKING:
    print "[L]inear masking is ENABLED"
    print "[N]onlinear masking is DISABLED"

    op_xor = LIN_xor
    op_and = LIN_and
    op_not = LIN_not
    op_share = LIN_initial_share
    op_decode = LIN_decode
else:
    print "[L]inear masking is ENABLED"
    print "[N]onlinear masking is ENABLED"

    op_xor = MINQ_xor
    op_and = MINQ_and
    op_not = MINQ_not
    op_share = MINQ_initial_share
    op_decode = MINQ_decode

shares = {}
for x in xbits:
    shares[x] = op_share(x)

itr = 0
for action, bit in co.code:
    itr += 1
    # if itr % 1000 == 0:
    #     print itr
    if action == "compute":
        if bit.op == OP.XOR:
            x, y = bit.args
            xs = shares[x]
            ys = shares[y]
            res = op_xor(xs, ys)
        elif bit.op == OP.AND:
            x, y = bit.args
            xs = shares[x]
            ys = shares[y]
            res = op_and(xs, ys)
        elif bit.op == OP.OR:
            x, y = bit.args
            xs = shares[x]
            ys = shares[y]
            res = op_xor(xs, op_xor(ys, op_and(xs, ys)))
        elif bit.op == OP.NOT:
            x, = bit.args
            xs = shares[x]
            res = op_not(xs)
        else:
            print `bit`, OP.name[bit.op], bit.args
            assert 0, "unknown op"
        shares[bit] = res

yfinal = [op_decode(shares[y]) for y in ybits]
print "Used", randused, "random bits"

print "Generating final code"
code = []
co = Orderer(xbits=xbits, ybits=yfinal).compile()

bit_id = {}
for i, x in enumerate(xbits):
    bit_id[x] = i

numrand = 0
maxid = 128
free = []
for action, bit in co.code:
    if action == "compute":
        if not free:
            free.append(maxid)
            maxid += 1
        bit_id[bit] = free.pop()

        if bit.op == OP.XOR:
            a, b = bit.args
            # code.append("m[%d] = m[%d] ^ m[%d];" % (bit_id[bit], bit_id[a], bit_id[b]))
            code.append(pack("=BHHH", 0, bit_id[bit], bit_id[a], bit_id[b]))
        elif bit.op == OP.AND:
            a, b = bit.args
            # code.append("m[%d] = m[%d] & m[%d];" % (bit_id[bit], bit_id[a], bit_id[b]))
            code.append(pack("=BHHH", 1, bit_id[bit], bit_id[a], bit_id[b]))
        elif bit.op == OP.OR:
            a, b = bit.args
            # code.append("m[%d] = m[%d] | m[%d];" % (bit_id[bit], bit_id[a], bit_id[b]))
            raise NotImplementedError("OR is not supported (should not appear here")
        elif bit.op == OP.NOT:
            a, = bit.args
            # code.append("m[%d] = m[%d] ^ 1;" % (bit_id[bit], bit_id[a]))
            code.append(pack("=BHH", 2, bit_id[bit], bit_id[a]))
        elif bit.op == OP.RANDOM:
            # code.append("m[%d] = randbit();" % bit_id[bit])
            code.append(pack("=BH", 3, bit_id[bit]))
            numrand += 1
        else:
            print `bit`, OP.name[bit.op], bit.args
            assert 0, "unknown op"
    elif action == "free":
        free.append(bit_id[bit])
    else:
        assert 0, action

print "Maximum state size:", maxid, "bits"

memlog = 1
while 2**memlog <= maxid:
    memlog += 1
assert maxid < 2**memlog

print "Memory usage:", "2^%d" % memlog, "=", 2**memlog, "bytes"

ct_poses = [bit_id[b] for b in yfinal]
opcodes = map(ord, "".join(code))
print "Opcode data size:", "%.2f" % (len(opcodes)/10**6.0), "MB"
print "Num opcodes:", len(code), "of which random:", numrand

src = open("build/template.c").read()
src = src.replace("$PLACE_MEMLOG", str(memlog))

# src = src.replace("CIRCUIT_CODE", "\n".join(code))
open("build/opcodes.bin", "w").write("".join(map(chr, opcodes)))

src = src.replace("$NUM_OPCODES", str(len(code)))
src = src.replace("$OPCODES_SIZE", str(len(opcodes)))

src = src.replace("$CT_POSES", ",".join(map(str, ct_poses)))

open("build/code.c", "w").write(src)

print "=========="
