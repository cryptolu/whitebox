#-*- coding:utf-8 -*-

from itertools import product
from collections import defaultdict

from random import choice, randint

def sbin(x, n):
    return "".join(map(str, tobin(x, n)))

def tobin(x, n):
    return tuple(map(int, bin(x).lstrip("0b").rjust(n, "0")))

def frombin(v):
    return int("".join(map(str, v)), 2 )

def hamming(x):
    ans = 0
    while x:
        ans += x & 1
        x >>= 1
    return ans

hw = hamming
