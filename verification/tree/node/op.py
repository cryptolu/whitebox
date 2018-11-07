#-*- coding:utf-8 -*-

import operator

class OP(object):
    OPS = {}

    def __init__(self):
        self.free_id = 0

        self.name = {}
        self.arity = {}

        self.operator = {}
        self.symbol = {}
        self.symmetric = {}

        for name, data in self.OPS.items():
            self.add_op(name, data)

    def add_op(self, name, data):
        name = name.upper()
        opnum = data.get("id", self.free_id)
        self.free_id = max(self.free_id, opnum + 1)

        setattr(self, name, opnum)
        for alias in data.get("aliases", ()):
            setattr(self, alias, opnum)

        self.name[opnum] = name
        self.arity[opnum] = int(data["arity"])

        self.process_data(opnum, name, data)

    def process_data(self, opnum, name, data):
        self.operator[opnum] = data.get("operator", None)
        self.symbol[opnum] = data.get("symbol", None)
        self.symmetric[opnum] = data.get("symmetric", False)

    def eval(self, op, args):
        if not self.operator[op]:
            raise NotImplementedError("Operator %s can not be evaluated" % self.name[op])
        return self.operator[op](*args)


class BitOP(OP):
    OPS = dict(
        XOR=dict(operator=operator.xor,
                 symbol="^",
                 symmetric=True,
                 arity=2),
        AND=dict(operator=operator.and_,
                 symbol="&",
                 symmetric=True,
                 arity=2),
        OR =dict(operator=operator.or_,
                 symbol="|",
                 symmetric=True,
                 arity=2),

        NOT=dict(operator=lambda a: ~a,
                 symbol="~",
                 arity=2),

        ZERO=dict(operator=lambda: 0,
                  symbol="0",
                  arity=0),
        ONE =dict(operator=lambda: 1,
                  symbol="1",
                  arity=0),

        INPUT =dict(operator=None,
                    symbol="x",
                    arity=0),
        OUTPUT=dict(operator=lambda a: a,
                    symbol="@",
                    arity=1),
    )

