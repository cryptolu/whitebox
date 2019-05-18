#-*- coding:utf-8 -*-

from ops import OP

class Bit(object):
    COUNTER = 0

    meta = {}

    def __init__(self, op, *args, **kwargs):
        self.op = op
        self.args = list(args)
        self.meta = self.meta.copy()
        self.meta.update(kwargs)
        self._h = None

        if self.op in (OP.ONE, OP.ZERO):
            self.id = float("+inf")
        else:
            self.id = self.COUNTER
            type(self).COUNTER += 1

    def make_func(op):
        if op in OP.symmetric:
            def f(a, b):
                if isinstance(b, int) or isinstance(b, long):
                    if b & 1 == OP.neutral.get(op, None):
                        # print "NEUT"
                        return a
                    if b & 1 == 1 and op == OP.XOR:
                        # print "XOR 1 = NOT"
                        return ~a
                    b = Bit(OP.ONE) if b & 1 else Bit(OP.ZERO)
                    return Bit(op, a, b)
                elif b.is_const() and b.const() == OP.neutral.get(op, None): return a
                elif a.is_const() and a.const() == OP.neutral.get(op, None): return b

                # WARNING: added later..
                elif a.op == OP.ZERO and op == OP.AND: return Bit.ZERO
                elif b.op == OP.ZERO and op == OP.AND: return Bit.ZERO
                elif a.op == OP.ONE and op == OP.OR: return Bit.ONE
                elif b.op == OP.ONE and op == OP.OR: return Bit.ONE

                # WARNING: too optimizing?
                elif op == OP.XOR and a.is_const() and b.is_const(): return Bit.make_const(a.const() ^ b.const())
                elif op == OP.AND and a.is_const() and b.is_const(): return Bit.make_const(a.const() & b.const())
                elif op == OP.OR and a.is_const() and b.is_const(): return Bit.make_const(a.const() | b.const())
                elif op == OP.XOR and b.op == OP.ONE: return ~a
                elif op == OP.XOR and a.op == OP.ONE: return ~b
                return Bit(op, a, b)
        else:
            def f(a, b):
                return Bit(op, a, b)
        return f
    Xor = __xor__ = __rxor__ = make_func(OP.XOR)
    And = __and__ = __rand__ = make_func(OP.AND)
    Or = __or__ = __ror__ = make_func(OP.OR)
    Nxor = make_func(OP.NXOR)
    Nand = make_func(OP.NAND)
    Nor = make_func(OP.NOR)

    def __invert__(self):
        if self.op == OP.NOT:
            return self.args[0]
        if self.is_const():
            if self.op == OP.ONE:
                return Bit(OP.ZERO)
            else:
                return Bit(OP.ONE)
        return Bit(OP.NOT, self)

    def __str__(self):
        if self.op == OP.INPUT: return str(self.args[0])
        if self.op == OP.ONE: return "1"
        if self.op == OP.ZERO: return "0"
        if self.args:
            return "(" +  (" " + OP.name[self.op] + " ").join(map(str, self.args)) + ")"
        return OP.name[self.op]

    def eval(self, input, acc=None):
        if acc is None:
            acc = {}
        if self not in acc:
            if self.op == OP.INPUT:
                acc[self] = input[self.args[0]]
            else:
                acc[self] = OP.eval(self.op, [v.eval(input, acc=acc) for v in self.args])
        return acc[self]

    def flatten(self, out=None):
        if out is None:
            out = set()
        if self in out:
            return
        if self.op != OP.INPUT:
            for bit in self.args:
                bit.flatten(out=out)
        out.add(self)
        return out

    def __hash__(self):
        return hash(id(self))
        return hash(self.id)
        if self._h is None:
            self._h = hash((self.op,) + tuple(hash(v) for v in self.args))
        return self._h

    def function_hash(self):
        return hash(self)
    # def __eq__(self, other):
        # return hash(self) == hash(other)

    def is_const(self):
        return self.op in (OP.ONE, OP.ZERO)

    def is_input(self):
        return self.op == OP.INPUT

    def is_primitive(self):
        return self.op in OP.primitive

    def const(self):
        assert self.op in (OP.ONE, OP.ZERO)
        return int(self.op == OP.ONE)

    @classmethod
    def make_const(self, v):
        return Bit(OP.ONE) if v else Bit(OP.ZERO)

Bit.ONE = Bit(OP.ONE)
Bit.ZERO = Bit(OP.ZERO)

def BitVar(name):
    return Bit(OP.INPUT, name)

def VarVec(name, n):
    # return [BitVar(name % i) for i in xrange(n)]
    return [BitVar((name, i)) for i in xrange(n)]

if __name__ == '__main__':
    x = [Bit(OP.INPUT, i) for i in xrange(8)]
    y = ~(x[0] ^ x[1] & x[2])
    for v in y.flatten():
        print v

    y = ~(x[0] ^ x[1] & x[2])
    assert 1 == y.eval({0: 1, 1: 1, 2: 1})
    y = (x[0] ^ x[1] & x[2])
    assert 0 == y.eval({0: 1, 1: 1, 2: 1})
