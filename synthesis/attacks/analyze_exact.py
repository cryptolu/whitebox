#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import sys, os, string
from itertools import product
from collections import defaultdict

from sbox import sbox, rsbox
from reader import Reader


#== Configuration

# go from the end of the traces if we attack last S-Boxes ?
REVERSE = False # not supported yet

NTRACES = int(sys.argv[1])
WINDOW = int(sys.argv[2])
STEP = WINDOW
if len(sys.argv) >= 4:
    STEP = int(sys.argv[3])

R = Reader(ntraces=NTRACES,
           window=WINDOW,
           step=STEP,
           packed=True,
           reverse=REVERSE,
           dir="./traces")


STOP_ON_FIRST_MATCH = 0
ONE_CANDIDATE_PER_SBOX = True

# second order should break 1-st order linear masking
ENABLE_SECOND_ORDER = 1

# attack last S-Box?
CT_SIDE = REVERSE

# which/how many  S-Boxes to attack
BYTE_INDICES = range(16) # all
# BYTE_INDICES = range(3) # only first 3

# charset for key bytes
KS = range(256)
# KS = map(ord, string.printable) # only printable characters

# linear masks to check after S-Box, for example
# 0xff will try to match scalar_product(SBox(x xor k), 0b11111111)
# 1 matches the last output bit
LINS = (1, 2, 4, 8, 16, 32, 64, 127, 255)
LINS = (1,)
# LINS = range(1, 256)


def scalar_bin(a, b):
    v = a & b
    res = 0
    while v:
        res ^= v & 1
        v >>= 1
    return res

MASK = 2**R.ntraces - 1

print "Total traces:", R.ntraces, "of size", "%.1fK bits (%d)" % (R.trace_bytes / 1000.0, R.trace_bytes)

#== Generate predicted vectors from plaintext/ciphertext and key guess

targets = []
for si, lin, k in product(BYTE_INDICES, LINS, KS):
    target = 0
    for p, c in zip(R.pts, R.cts):
        if k is None:
            if CT_SIDE:
                x = ord(c[si])
            else:
                x = ord(p[si])
        else:
            if CT_SIDE:
                x = ord(c[si])
                x = rsbox[x ^ k]
            else:
                x = ord(p[si])
                x = sbox[x ^ k]
        target = (target << 1) | scalar_bin(x, lin)

    targets.append((target, (si, lin, k, 0)))
    targets.append((target ^ MASK, (si, lin, k, 1)))

print "Generated %d target vectors" % len(targets)

#== Read traces and analyze
for i_window, vectors in enumerate(R):
    print "Window %d" % (i_window+1), "/", R.num_windows,

    print "offset %d-%d (of %d)" % (R.offset*8, R.offset*8 + len(vectors), R.trace_bytes*8)
    print "   ", len(vectors), "vectors"

    vectors_rev = defaultdict(list)
    for off, v in enumerate(vectors):
        vectors_rev[v].append(R.offset + off)

    print "   ", len(vectors_rev), "unique vectors"
    print "   ", len(targets), "target vectors"

    candidates = [set() for _ in xrange(16)]
    key_found = False

    for target, kinfo in targets:
        si, lin, k, const1 = kinfo
        if ONE_CANDIDATE_PER_SBOX and candidates[si]:
            continue

        # single value
        if target in vectors_rev:
            print "MATCH (SINGLE):",
            print "sbox #%d," % si,
            print "lin.mask 0x%02x," % lin,
            print "key 0x%02x=%r," % (k, chr(k)),
            print "negated? %s," % bool(const1),
            # linear combination indexes (may be non-unique)
            inds = vectors_rev[target][:10]
            print "indexes", "(%d total)" % len(vectors_rev[target]), inds,
            print

            candidates[si].add(k)
            key_found = True

        if ENABLE_SECOND_ORDER:
            # shared in 2 shares
            for v1 in vectors_rev:
                if v1 in (0, MASK):
                    continue
                v2 = target ^ v1
                if v2 in vectors_rev:
                    print "MATCH (DOUBLE):",
                    print "sbox #%d," % si,
                    print "lin.mask 0x%02x," % lin,
                    print "key 0x%02x=%r," % (k, chr(k)),
                    print "negated? %s," % bool(const1),
                    # linear combination indexes (may be non-unique)
                    inds1 = vectors_rev[v1][:5]
                    inds2 = vectors_rev[v2][:5]
                    print "indexes", "(%d and %d total)" % (len(vectors_rev[v1]), len(vectors_rev[v2])), inds1, inds2
                    print

                    candidates[si].add(k)
                    key_found = True

                    print "   ", "   ", [divmod(v, 8) for v in vectors_rev[v1][:10]]
                    print "   ", "   ", [divmod(v, 8) for v in vectors_rev[v2][:10]]
                    print

                    candidates[si].add(k)
                    key_found = True

    if key_found:
        print
        print "Key candidates found:"
        for si, cands in enumerate(candidates):
            if cands:
                print "S-Box #%d: %s" % (si, ",".join("0x%02x(%r)" % (c, chr(c)) for c in cands))
        print

    if key_found and STOP_ON_FIRST_MATCH:
        quit()


