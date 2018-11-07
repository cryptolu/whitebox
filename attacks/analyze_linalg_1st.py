#!/usr/bin/env sage
#-*- coding:utf-8 -*-

from sage.all import *

import sys, os, string
from itertools import product

from sbox import sbox, rsbox
from reader import Reader


#== Configuration

NTRACES = int(sys.argv[1])
WINDOW = int(sys.argv[2])
assert NTRACES > WINDOW, "window should be smaller than number of traces to avoid false-positives"

STEP = WINDOW / 4

STOP_ON_FIRST_MATCH = 0

# attack last S-Box?
CT_SIDE = 0
# go from the end of the traces if we attack last S-Boxes
REVERSE = CT_SIDE


# which/how many  S-Boxes to attack
# BYTE_INDICES = range(16) # all
BYTE_INDICES = range(3) # only first 3

# charset for key bytes
KS = range(256)
# KS = map(ord, string.printable) # only printable characters

# linear masks to check after S-Box, for example
# 0xff will try to match scalar_product(SBox(x xor k), 0b11111111)
# 1 matches the last output bit
LINS = (1,)



def tobin(x, n):
    return tuple(map(int, bin(x).lstrip("0b").rjust(n, "0")))

def scalar_bin(a, b):
    return int(Integer(a & b).popcount())

MASK = 2**NTRACES - 1
VECMASK = vector(GF(2), [1] * NTRACES)


#== Read plaintexts/ciphertexts and prepare trace readers

pts = []
cts = []
readers = []

for i in xrange(NTRACES):
    f_trace = "./traces/%04d.bin" % i
    f_pt = "./traces/%04d.pt" % i
    f_ct = "./traces/%04d.ct" % i
    pt = open(f_pt).read()
    ct = open(f_ct).read()
    pts.append(pt)
    cts.append(ct)
    readers.append(Reader(f_trace, reverse=REVERSE, window=WINDOW, step=STEP))

traces_size = os.stat(f_trace).st_size
print "Total traces:", NTRACES, "of size", "%.1fK (%d)" % (traces_size / 1000.0, traces_size)


#== Generate predicted vectors from plaintext/ciphertext and key guess

targets = []
for si, lin, k in product(BYTE_INDICES, LINS, KS):
    target = []
    for p, c in zip(pts, cts):
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
        target.append(scalar_bin(x, lin))
    assert len(target) == NTRACES
    target = vector(GF(2), target)
    targets.append((target, (si, lin, k, 0)))
    targets.append((target + VECMASK, (si, lin, k, 1)))

print "Generated %d target vectors" % len(targets)

target_mat = matrix(GF(2), [target for target, kinfo in targets])

#== Read traces and analyze

n_windows = (traces_size - WINDOW - 1) / STEP
i_window = 0
while 1:
    i_window += 1
    if REVERSE:
        print "Window %d" % (n_windows - i_window + 1), "/", n_windows,
    else:
        print "Window %d" % i_window, "/", n_windows,

    vectors = []
    for i_reader, reader in enumerate(readers):
        try:
            wnd_off, wnd = next(reader)
        except StopIteration:
            print "No window %d for reader %d (Finished?)" % (i_window, i_reader)
            quit()
        assert wnd

        # not sure if working with longs is faster than with arrays or Sage's vectors..
        if not vectors:
            vectors = [0 for _ in xrange(len(wnd))]
        for i, b in enumerate(wnd):
            val = ord(b) & 1
            vectors[i] = (vectors[i] << 1) | val

    print "offset %d-%d" % (wnd_off, wnd_off+WINDOW-1)
    print "   ", len(vectors), "vectors"

    vectors_rev = set(vectors)
    print "   ", len(vectors_rev), "unique vectors"
    print "   ", len(targets), "target vectors"

    candidates = [set() for _ in xrange(16)]
    key_found = False

    columns = [list(tobin(vec, NTRACES)) for vec in vectors_rev if vec not in (0, MASK)]
    mat = matrix(GF(2), columns)

    # trick to use kernel of M for quick verification of solution
    parity_checker = mat.right_kernel().matrix().transpose()
    check = target_mat * parity_checker
    check = map(bool, check.rows())
    for parity, (target, kinfo) in zip(check, targets):
        if parity:
            continue

        # can be done more efficiently using LU factors of mat (shared with left_kernel)
        # but happens only when the key is found
        # so optimization is not necessary
        sol = mat.solve_left(target)
        # assert sol * mat == target

        si, lin, k, const1 = kinfo
        print "MATCH:",
        print "sbox #%d," % si,
        print "lin.mask 0x%02x," % lin,
        print "key 0x%02x=%r," % (k, chr(k)),
        print "negated? %s," % bool(const1),
        # linear combination indexes (may be non-unique)
        inds = [wnd_off + i for i, take in enumerate(sol) if take]
        print "indexes", "%d...%d (distance %d)" % (min(inds), max(inds), max(inds)-min(inds)), inds,
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


