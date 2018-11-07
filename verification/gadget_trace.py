#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import math
from itertools import product

from tree import OptBitNode as Bit
from tree.trace import circuit_trace
from tree.anf import compute_anfs
OP = Bit.OP

from minimalist3 import Minimalist3

S = Minimalist3()

print S
print

x = Bit.inputs("x", S.N)
y = Bit.inputs("y", S.N)
rx = Bit.inputs("rx", S.NR)
ry = Bit.inputs("ry", S.NR)

# Any circuit can be put in target, not necessarily a masking scheme

# single operation
# target = S.EvalXOR(x, y, rx, ry)
# target = S.EvalAND(x, y, rx, ry)

# two at the same time (equivalent to previous two)
target = S.EvalXOR(x, y, rx, ry) + S.EvalAND(x, y, rx, ry)

# testing refresh separately
# target = S.Refresh(*(x + rx)) + S.Refresh(*(y+ry))


if 1: # compute ANFs and bias bound
    for bit in target:
        compute_anfs(bit)
    nodes = Bit.flatten_many(target)

    maxdeg = 0
    res = []
    for b in sorted(nodes, key=lambda b: b.id):
        if b.op in (b.OP.AND, b.OP.OR):
            print b.id, "=", b.OP.name[b.op], " ".join(map(str, [sub.id for sub in b.args if isinstance(sub, Bit)])), ":",
            print "degree on r %d, full %d:" % (b.meta["anf"].degree(filter_func=lambda v: v.startswith("r")), b.meta["anf"].degree()),
            print b.meta["anf"]
            res.append(b.meta["anf"])
        elif b.is_input():
            print b.id, "=", b.name(), ":", b.meta["anf"]
            res.append(b.meta["anf"])
        else:
            assert b.op in (b.OP.XOR, b.OP.NOT, b.OP.INPUT)

    print

    maxdeg = max(a.degree(filter_func=lambda v: v.startswith("r")) for a in res)
    from fractions import Fraction
    print "------------------------------------------"
    print "Maximum degree:", maxdeg
    bias = Fraction(1, 2)-Fraction(1, 2**maxdeg)
    print "Bias bound: bias <= %s" % bias
    e = -math.log(0.5 + bias, 2)
    print "Provable security:"
    try:
        print " 80 bit: R > %d" % (80 * (1 + 1/e))
        print "128 bit: R > %d" % (128 * (1 + 1/e))
    except:
        pass
    print "------------------------------------------"
    print

def sbin(x, n):
    return "".join(map(str, tobin(x, n)))

def tobin(x, n):
    return tuple(map(int, bin(x).lstrip("0b").rjust(n, "0")))

if 1: # trace the circuit to perform linear algebra analysis in Sage
    input_order = x + y + rx + ry
    inputs = list(product(range(2), repeat=len(input_order)))

    trace = circuit_trace(outputs=target, input_order=input_order, inputs_list=inputs)

    ntraces = len(inputs)
    order = sorted(trace.keys(), key=lambda bit: bit.id)
    order = [b for b in order if b.op != b.OP.XOR and not b.is_const()]

    with open("traces/%s" % S.NAME, "w") as f:
        with open("traces/%s.names" % S.NAME, "w") as fi:
            cntr = 0
            for bit in order:
                if bit.is_input():
                    name = bit.name()
                else:
                    name ="v%d" % cntr
                    cntr += 1
                value = trace[bit]
                f.write("%s`%s\n" % (name, sbin(value, ntraces)))

                info = bit.meta.get("tag", "") + ":"# + str(bit)
                info = info.strip(":")
                fi.write("%s`%s\n" % (name, info))

    print "Traces written"
