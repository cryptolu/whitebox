#-*- coding:utf-8 -*-

from symbolic import Bit, Var, Const

def compute_anfs(bit):
    if bit.is_input():
        bit.meta["anf"] = Bit(Var(bit.name()))
        return

    if bit.is_const():
        bit.meta["anf"] = Bit(Const(bit.value()))
        return

    TreeBit = bit.__class__
    res = []
    for sub in bit.args:
        if isinstance(sub, TreeBit) and "anf" not in sub.meta:
            compute_anfs(sub)
        res.append(sub.meta["anf"])
    bit.meta["anf"] = bit.OP.eval(bit.op, res)
