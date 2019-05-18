#-*- coding:utf-8 -*-


class Node(object):
    COUNTER = 0
    OP = NotImplemented

    meta = {}

    def __init__(self, op, *args, **kwargs):
        self.op = op
        self.args = list(args)
        self.meta = self.meta.copy()
        self.meta.update(kwargs)

        self.id = self.COUNTER
        type(self).COUNTER += 1

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def __iter__(self):
        for sub in self.args:
            if isinstance(sub, Node):
                yield sub

    def __str__(self):
        if self.op == self.OP.INPUT: return str(self.args[0])
        if self.meta.get("fake-input"): return self.meta.get("fake-input")
        sym = str(self.OP.symbol[self.op])

        if len(self.args) > 1:
            return "(" +  (" " + sym + " ").join(map(str, self.args)) + ")"
        elif len(self.args) == 1:
            return sym + str(self.args[0])
        elif len(self.args) == 0:
            return sym

    def __hash__(self):
        return hash(id(self))

    def structure_hash(self):
        if self.__dict__.get("_sh", None) is None:
            self._sh = hash((self.op,) + tuple(hash(v) for v in self.args))
        return self._sh

    def is_input(self):
        return self.op == self.OP.INPUT

    @classmethod
    def input(cls, name):
        return cls(cls.OP.INPUT, name)

    @classmethod
    def inputs(cls, name, n, tostr=True):
        return tuple(cls.input(name+str(i) if tostr else (name, i)) for i in xrange(n))

    def name(self):
        assert self.is_input()
        return self.args[0]

    def flatten(self, out=None):
        if out is None:
            out = set()
        if self in out:
            return
        for sub in self.args:
            if isinstance(sub, Node):
                sub.flatten(out=out)
        out.add(self)
        return out

    @staticmethod
    def flatten_many(nodes):
        out = set()
        for node in nodes:
            node.flatten(out=out)
        return out

    def eval(self, acc):
        """acc is dict {bit: value} with initial values (typically input bits)"""
        if self not in acc:
            acc[self] = self.OP.eval(self.op, [v.eval(acc) for v in self.args])
        return acc[self]
