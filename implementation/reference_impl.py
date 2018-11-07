#!/usr/bin/env python2
#-*- coding:utf-8 -*-

from Crypto.Cipher import AES

k = open("key").read()[:16]

pt = open("test_plaintext").read()
ct = AES.new(k).encrypt(pt)
open("test_ciphertext", "w").write(ct)

print "key:       ", k.encode("hex"), `k`
print "plaintext: ", pt.encode("hex"), `pt`
print "ciphertext:", ct.encode("hex"), `ct`
