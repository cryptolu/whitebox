# AES implementation

This folder contains a bitwise **AES-128** implementation protected with the *minimalist quadratic masking* scheme from the paper and a first-order linear masking scheme.

**It is a masking proof-of-concept and NOT a secure white-box implementation!**

### How to run:

1. Put an AES-128 key in the file `key`
2. Run `./generate.py` to generate the source code file `build/code.c` together with the opcode table `/build/opcodes.bin`.
3. Run `./buildrun.sh` to compile and test the implementation by encrypting the file `test_plaintext`.

It is preferable to use PyPy for performance reasons.

To manually run the compiled program set the `OPCODES` environment variable to the path to the opcode table file (e.g. `build/opcodes.bin`) and run the program with the plaintext in the standard input (stdin).

### Options:

1. Set the `TRACE` environment variable to the path where all computed values should be recorded. This allows to produce computational traces for DCA attacks.
1. Set `DISABLE_NONLINEAR_MASKING` environment variable to 1 (during **compilation**). Then only the first-order linear masking is used.
1. Set `DISABLE_RANDOM` environment variable to 1 (during **execution**). Then the randomness is replaced by constants.

### Example

```
$ DISABLE_NONLINEAR_MASKING=0 pypy generate.py
Building circuit for 10 rounds of AES
:: circuit walk
:: ordering 31783 nodes
:: code size: 63343 operations
Masking 63343 events
[L]inear masking is ENABLED
[N]onlinear masking is ENABLED
Used 409664 random bits
Generating final code
:: circuit walk
:: ordering 2588871 nodes
:: code size: 5177486 operations
Maximum state size: 926 bits
Memory usage: 2^10 = 1024 bytes
Opcode data size: 16.47 MB
Num opcodes: 2588743 of which random: 409664
(Time: ~15 seconds)
==========
$ ./buildrun.sh
Encrypting...

real    0m0.193s
user    0m0.185s
sys     0m0.008s

Ciphertext:
00000000: 47e8 c363 429a 5f3a dec2 12ed 3b38 2157  G..cB._:....;8!W
00000010: 29cc c6d3 dc02 fd64 1244 e00b 2d53 1a86  )......d.D..-S..
00000020: 9a62 043a c28d 2f79 0091 1395 9458 0d13  .b.:../y.....X..
00000030: a65f e8ef b243 4c67 fe8c 0864 851e e622  ._...CLg...d..."
00000040: b356 1bf9 6f9c 0fd9 7217 8305 e4a5 ca77  .V..o...r......w
00000050: cec6 074e 7bb9 e27d 2699 a8fd 8798 9f0a  ...N{..}&.......
00000060: 6eed 52fc 79ec 82cb e0eb c5a1 1789 4a2d  n.R.y.........J-
00000070: c608 e021 222b a499 613a cb46 d934 bb33  ...!"+..a:.F.4.3

Difference:
==========
```
