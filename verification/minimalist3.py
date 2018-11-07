#-*- coding:utf-8 -*-

class Scheme(object):
    N = NotImplemented
    NR = NotImplemented
    NAME = NotImplemented

    def __str__(self):
        return "<Scheme %s N=%d NR=%d>" % (self.NAME, self.N, self.NR)

class Minimalist3(Scheme):
    N = 3
    NR = 3
    NAME = "minimalist3"

    def Decode(self, x):
        a, b, c = x
        return (a & b) ^ c

    def Refresh(self, x, y, z, rx, ry, rr):
        if 1: # secure
            xrr = x ^ rr
            yrr = y ^ rr
            rz = (rx & yrr) ^ (ry & xrr) ^ ((rx ^ rr) & (ry ^ rr)) ^ rr
        else: # insecure
            rz = (rx & y) ^ (ry & x) ^ (rx & ry)

        x ^= rx
        y ^= ry
        z ^= rz
        return x, y, z

    def EvalXOR(self, x, y, rx, ry):
        x = self.Refresh(*(x + rx))
        y = self.Refresh(*(y + ry))

        a, b, c = x
        d, e, f = y
        ae = a & e
        bd = b & d
        a_d = a ^ d
        b_e = b ^ e
        x = a_d
        y = b_e
        z = c ^ f ^ ae ^ bd
        return x, y, z

    def EvalAND(self, x, y, rx, ry):
        zero = rx[0] ^ rx[0]
        x = self.Refresh(*(x + rx))
        y = self.Refresh(*(y + ry))

        a, b, c = x
        d, e, f = y

        rf = ry[2]
        rc = rx[2]
        # rf = rc = zero # introduces another insecurity

        x = (a & e) ^ rf
        y = (b & d) ^ rc

        triple1 = ((c & e) ^ (b & rf)) & d
        triple2 = ((b & f) ^ (e & rc)) & a
        double = c & f
        fix = rf & rc

        z = triple1 ^ triple2 ^ double ^ fix
        return x, y, z
