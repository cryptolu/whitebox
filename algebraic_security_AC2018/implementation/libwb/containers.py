#-*- coding:utf-8 -*-

import operator

class Vector(list):
    ZERO = 0
    WIDTH = None

    @classmethod
    def make(cls, lst):
        lst = list(lst)
        if cls.WIDTH is not None:
            assert len(lst) == cls.WIDTH
        return cls(lst)

    def split(self, n=2):
        assert len(self) % n == 0
        w = len(self) // n
        return Vector(self.make(self[i:i+w]) for i in xrange(0, len(self), w))

    def concat(self, *lst):
        v = list(self)
        for t in lst:
            v += list(t)
        return self.make(v)

    def rol(self, n=1):
        n %= len(self)
        return self.make(self[n:] + self[:n])

    def ror(self, n=1):
        return self.rol(-n)

    def shl(self, n=1):
        assert n >= 0
        n = min(n, len(self))
        return self.make(list(self[n:]) + [self._zero() for i in xrange(n)])

    def shr(self, n=1):
        assert n >= 0
        n = min(n, len(self))
        return self.make([self._zero() for i in xrange(n)] + list(self[:-n]))

    def _zero(self):
        """method because sometimes need different instances"""
        return self.ZERO

    def __repr__(self):
        return "<Vector len=%d list=%r>" % (len(self), list(self))

    def flatten(self):
        if isinstance(self[0], Vector):
            return self[0].concat(*self[1:])
        return reduce(operator.add, list(self))

    def permute(self, perm, inverse=False):
        """
        Perm contains indexes in original vector
        Example:
        vec  = [0, 1, 2, 3]
        perm = [1, 2, 3, 0]
        res  = [1, 2, 3, 0]
        """
        if not inverse:
            lst = [self[i] for i in perm]
        else:
            lst = [None] * len(self)
            for i, j in enumerate(perm):
                lst[j] = self[i]
        return self.make(lst)

    def map(self, f, with_coord=False):
        if with_coord:
            return self.make(f(i, v) for i, v in enumerate(self))
        else:
            return self.make(f(v) for v in self)

    def __xor__(self, other):
        assert isinstance(other, Vector)
        assert len(self) == len(other)
        return self.make(a ^ b for a, b in zip(self, other))

    def __or__(self, other):
        assert isinstance(other, Vector)
        assert len(self) == len(other)
        return self.make(a | b for a, b in zip(self, other))

    def __and__(self, other):
        assert isinstance(other, Vector)
        assert len(self) == len(other)
        return self.make(a & b for a, b in zip(self, other))

    def set(self, x, val):
        return self.make(v if i != x else val for i, v in enumerate(self))


class Rect(object):
    def __init__(self, vec, h=None, w=None):
        assert h or w
        if h:
            w = len(vec) // h
        elif w:
            h = len(vec) // w
        assert w * h == len(vec)
        self.w, self.h = w, h

        self.lst = []
        for i in xrange(0, len(vec), w):
            self.lst.append(list(vec[i:i+w]))

    @classmethod
    def from_rect(cls, rect):
        self = object.__new__(cls)
        self.lst = rect
        self.h = len(rect)
        self.w = len(rect[0])
        return self

    def __getitem__(self, pos):
        y, x = pos
        return self.lst[y][x]

    def __setitem__(self, pos, val):
        y, x = pos
        self.lst[y][x] = val

    def row(self, i):
        return Vector(self.lst[i])

    def col(self, i):
        return Vector(self.lst[y][i] for y in xrange(self.h))

    def diag(self, x):
        assert self.w == self.h
        return Vector(self.lst[i][(x+i) % self.w] for i in xrange(self.h))

    def set_row(self, y, vec):
        for x in xrange(self.w):
            self.lst[y][x] = vec[x]
        return self

    def set_col(self, x, vec):
        for y in xrange(self.h):
            self.lst[y][x] = vec[y]
        return self

    def set_diag(self, x, vec):
        assert self.w == self.h
        for i in xrange(self.h):
            self.lst[i][(x+i) % self.w] = vec[i]
        return self

    def apply(self, f, with_coord=False):
        for y in xrange(self.h):
            if with_coord:
                self.lst[y] = [f(y, x, v) for x, v in enumerate(self.lst[y])]
            else:
                self.lst[y] = map(f, self.lst[y])
        return self

    def apply_row(self, x, func):
        return self.set_row(x, func(self.row(x)))

    def apply_col(self, x, func):
        return self.set_col(x, func(self.col(x)))

    def apply_diag(self, x, func):
        assert self.w == self.h
        return self.set_diag(x, func(self.diag(x)))

    def flatten(self):
        lst = []
        for v in self.lst:
            lst += v
        return Vector(lst)

    def zipwith(self, f, other):
        assert isinstance(other, Rect)
        assert self.h == other.h
        assert self.w == other.w
        return Rect(
            [f(a, b) for a, b in zip(self.flatten(), other.flatten())],
            h=self.h, w=self.w
        )


    def transpose(self):
        rect = [[self.lst[y][x] for y in xrange(self.h)] for x in xrange(self.w)]
        return Rect.from_rect(rect=rect)

    def __repr__(self):
        return "<Rect %dx%d>" % (self.h, self.w)
