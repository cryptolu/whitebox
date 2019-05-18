#-*- coding:utf-8 -*-

import operator

class OP(object):
    name = {}
    symmetric = set()
    primitive = set()
    operators = {}
    neutral = {}
    c_op = {}

    def eval(self, op, args):
        assert op != self.INPUT
        if op not in self.operators:
            from pprint import pprint
            raise KeyError, (self.name[op], op)
        if len(args) > 1:
            return reduce(self.operators[op], args)
        elif len(args) == 1:
            return self.operators[op](args[0])
        elif len(args) == 0:
            return self.operators[op]()
        else:
            assert False

OP = OP()

OPERATORS = dict(
    XOR=operator.xor,
    AND=operator.and_,
    OR=operator.or_,
    NXOR=lambda a,b: a^b^1,
    NAND=lambda a,b: a&b^1,
    NOR=lambda a,b: a|b^1,
    NOT=lambda a: a^1,
    ORNOT=lambda a: a|(b^1),
    ANDNOT=lambda a: a&(b^1),

    ZERO=lambda: 0,
    ONE=lambda: 1,

    RANDOM=None,
    INPUT=None,
)
OPS_SYMMETRIC = "XOR AND OR NXOR NAND NOR".split()
OPS_PRIMITIVE = "ONE ZERO INPUT".split()
OPS_NEUTRAL = dict(XOR=0, AND=1, OR=0)
OPS_C_OP = dict(
    XOR=lambda args: "^".join(args),
    AND=lambda args: "&".join(args),
    OR=lambda args: "|".join(args),
    NOT=lambda args: "~" + args[0],
)


for opnum, name in enumerate(OPERATORS):
    setattr(OP, name, opnum)
    OP.name[opnum] = name
    OP.operators[opnum] = OPERATORS[name]

for opname, val in OPS_NEUTRAL.items():
    OP.neutral[getattr(OP, opname)] = val

for opname, val in OPS_C_OP.items():
    OP.c_op[getattr(OP, opname)] = val

for opname in OPS_SYMMETRIC:
    OP.symmetric.add(getattr(OP, opname))
for opname in OPS_PRIMITIVE:
    OP.primitive.add(getattr(OP, opname))


