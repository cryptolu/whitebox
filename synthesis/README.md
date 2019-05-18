# Synthesis Tools for White-box Implementations

This repository contains a framework for creating and analysing circuit-based white-box implementations. It was presented at the [Whib0x 2019](https://www.cryptoexperts.com/whibox2019/) workshop and is based on the code from the [White-box Tools](https://github.com/cryptolu/whitebox) repository of the paper [Attacks and Countermeasures for White-box Designs](https://eprint.iacr.org/2018/049) by Alex Biryukov and Aleksei Udovenko ([ASIACRYPT 2018](https://www.springer.com/gp/book/9783030033286)).

[Slides](./slides.pdf) from the workshop are available.

**Requirements**: Python2, [SageMath](http://www.sagemath.org/), [PyPy2](https://pypy.org/) (recommended). Python 3 support may be added soon.

## Minimal example:

AES circuit with *configurable* masking (quadratic MINQ + linear DOM-indep).

```python
from whitebox import Bit
from whitebox.utils import str2bin
NR = 10
KEY = "MySecretKey!2019"

from whitebox.ciphers.AES import BitAES
pt = Bit.inputs("pt", 128)
ct, k10 = BitAES(pt, Bit.consts(str2bin(KEY)), rounds=NR)

from whitebox.prng import LFSR, Pool
prng = LFSR(taps=[0, 2, 5, 18, 39, 100, 127],
            state=BitAES(pt, pt, rounds=2)[0])
rand = Pool(n=128, prng=prng).step

from whitebox.masking import MINQ, DOM, mask_circuit
ct = mask_circuit(ct, MINQ(rand=rand))
ct = mask_circuit(ct, DOM(rand=rand, nshares=2))

from whitebox.whibox import whibox_generate
whibox_generate(ct, "build/submit.c", "Hello, world!")
```
