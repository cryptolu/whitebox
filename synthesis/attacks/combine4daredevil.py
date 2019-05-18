#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import sys
import os

n = int(sys.argv[1])
packed = True

pts = []
cts = []

out_pt = open("./traces/all.input", "w")
out_ct = open("./traces/all.output", "w")
out_t = open("./traces/all.bin", "w")

nsamples = None

def expand_byte(b):
    res = []
    b = ord(b)
    for i in xrange(8):
        res.append("\x00\x01"[(b >> (7 - i & 7)) & 1])
    return "".join(res)

for i in xrange(n):
    fpt = "./traces/%04d.pt" % i
    fct = "./traces/%04d.ct" % i
    ft = "./traces/%04d.bin" % i

    with open(fpt) as f: pt = f.read(16)
    with open(fct) as f: ct = f.read(16)
    with open(ft) as f: trace = f.read()
    if packed:
        trace = "".join(map(expand_byte, trace))

    if nsamples is None:
        nsamples = len(trace)
    else:
        assert nsamples == len(trace)

    out_pt.write(pt)
    out_ct.write(ct)
    out_t.write(trace)

print n, "traces"

config = """
[Traces]
files=1
trace_type=i
transpose=true
index=0
nsamples=%(nsamples)d
trace=traces/all.bin %(n)d %(nsamples)d

[Guesses]
files=1
guess_type=u
transpose=true
guess=traces/all.input %(n)d 16

[General]
threads=8
order=1
//window=0
return_type=double
algorithm=AES
position=attacks/AES_AFTER_SBOX
round=0
bitnum=0
bytenum=all
//correct_key=???
memory=16G
top=20
""" % dict(nsamples=nsamples, n=n)

with open("daredevil.config", "w") as f:
    f.write(config)
