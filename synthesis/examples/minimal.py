#-*- coding:utf-8 -*-

import os
from whitebox.tree.node import OptBitNode as Bit
from whitebox.utils import str2bin, bin2str

NR = 10
KEY = "MySecretKey!2019"

from whitebox.ciphers.AES import BitAES
pt = Bit.inputs("pt", 128)
ct, k10 = BitAES(pt, Bit.consts(str2bin(KEY)), rounds=NR)

from whitebox.prng import LFSR, Pool
prng = LFSR(taps=[0, 2, 5, 18, 39, 100, 127],
            state=BitAES(pt, pt[::-1], rounds=2)[0])
rand = Pool(n=128, prng=prng).step

from whitebox.masking import MINQ, DOM, mask_circuit
ct = mask_circuit(ct, MINQ(rand=rand))
ct = mask_circuit(ct, DOM(rand=rand, nshares=2))

# a) generate WhibOx submission
from whitebox.whibox import whibox_generate
whibox_generate(ct, "build/submit.c", "Ok, world!")

# b) compile circuit to file
from whitebox.serialize import RawSerializer
RawSerializer().serialize_to_file(ct, "circuits/aes10.bin")

# c) compute reference AES to verify correctness
from whitebox.ciphers.AES.aes import encrypt
pt = os.urandom(64)
ct = "".join(encrypt(pt[i:i+16], KEY, nr=NR) for i in xrange(0, len(pt), 16))
open("build/cipher", "w").write(ct)

