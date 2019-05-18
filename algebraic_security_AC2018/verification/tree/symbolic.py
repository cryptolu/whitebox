#-*- coding:utf-8 -*-

from itertools import chain

class Term(object): pass
class Const(Term, int): pass
class Var(Term, str): pass

class Bit(Term):
    def __init__(self, v):
        if isinstance(v, set):
            self.anf = v
        elif isinstance(v, Const) or isinstance(v, Var):
            self.anf = {(v,)}
        elif isinstance(v, int):
            self.anf = {(Const(v),)}
        elif isinstance(v, str):
            self.anf = {(Var(v),)}
        else:
            assert 0, "Bit(%s) = ?" % type(v)
        self.anf.discard((Const(0),))

    def __eq__(self, other):
        return self.anf == other.anf

    def __xor__(self, other):
        if not isinstance(other, Bit):
            other = Bit(other)
        return Bit(self.anf ^ other.anf)
    __add__ = __xor__

    def __and__(self, other):
        res = set()
        for t1 in self.anf:
            for t2 in other.anf:
                res ^= {self._merge_products(t1, t2)}
        return Bit(res)
    __mul__ = __and__

    def __invert__(self):
        return self ^ Bit(1)

    def __or__(self, other):
        return ~((~self) & (~other))

    def _merge_products(self, t1, t2):
        assert isinstance(t1, tuple)
        assert isinstance(t2, tuple)
        res = set()
        for t in chain(t1, t2):
            if isinstance(t, Const):
                if t == 0:
                    return (t,)
                continue
            elif isinstance(t, Var):
                res.add(t)
        if not res:
            return (Const(1),)
        return tuple(sorted(res))

    def __str__(self):
        res = []
        for t in self.anf:
            res.append( "*".join(map(str, sorted(t))) )
        return " ^ ".join(sorted(res)) or "0"

    def __repr__(self):
        return "Bit(%r)" % self.anf

    def degree(self, filter_func=None):
        if filter_func is None:
            return max(len(t) for t in self.anf) if self.anf else 0
        else:
            res = 0
            for t in self.anf:
                l = sum(1 for v in t if isinstance(v, Var) and filter_func(v))
                res = max(res, l)
            return res

    def variables(self, filter_func=None):
        vs = set()
        for t in self.anf:
            for v in t:
                if isinstance(v, Var) and (not filter_func or filter_func(v)):
                    vs.add(v)
        return vs

    def count(self, filter_func=None):
        return len(self.variables(filter_func=filter_func))

    def subs(self, var, bit):
        if isinstance(var, str):
            var = Var(var)
        assert isinstance(var, Var)
        assert isinstance(bit, Bit)
        res = self.anf.copy()
        for t1 in self.anf:
            if var in t1:
                res ^= {t1}
                t1 = list(t1)
                del t1[t1.index(var)]
                t1 = tuple(t1)
                for t2 in bit.anf:
                    res ^= {self._merge_products(t1, t2)}
        return Bit(res)


ZERO = Bit(0)
ONE = Bit(1)

if __name__ == '__main__':
    print Bit(Const(0))
    print Bit(Const(1))
    print Bit(Var("x1"))
    print Bit(Var("x2"))
    print Bit(Var("x1")) & Bit(Var("x2"))
    print Bit(Var("x1")) ^ Bit(Var("x2"))
    print Bit(1) * Bit("x1") * Bit("x2") * Bit(1) + Bit(0) * Bit("x3") + Bit(1)
    print (Bit("a") * Bit("b") + Bit("R") * Bit("b")).subs("b", Bit(1) + Bit("Q") + Bit("c") * Bit("b"))
    quit()
