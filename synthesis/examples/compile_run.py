#-*- coding:utf-8 -*-

from whitebox.tree.node import OptBitNode as Bit
from whitebox.utils import str2bin, bin2str
from whitebox.ciphers.AES import BitAES
from whitebox.serialize import RawSerializer
from whitebox.fastcircuit import FastCircuit

KEY = "MySecretKey!2019"

pt = Bit.inputs("pt", 128)
ct, k10 = BitAES(pt, Bit.consts(str2bin(KEY)), rounds=10)

# Encode circuit to file
RawSerializer().serialize_to_file(ct, "circuits/aes10.bin")

# Python API for C simulator
C = FastCircuit("circuits/aes10.bin")

ciphertext = C.compute_one("my_plaintext_abc")

# Verify correctness
from Crypto.Cipher import AES
ciphertext2 = AES.new(KEY).encrypt("my_plaintext_abc")
assert ciphertext == ciphertext2
