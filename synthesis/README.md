# Synthesis Tools for White-box Implementations

This repository contains a framework for creating and analysing circuit-based white-box implementations. It was presented at the [WhibOx 2019](https://www.cryptoexperts.com/whibox2019/) workshop and is based on the code from the [White-box Tools](https://github.com/cryptolu/whitebox) repository of the paper [Attacks and Countermeasures for White-box Designs](https://eprint.iacr.org/2018/049) by Alex Biryukov and Aleksei Udovenko ([ASIACRYPT 2018](https://www.springer.com/gp/book/9783030033286)).

[Slides](./slides.pdf) from the workshop are available.

This is an early version and may contain bugs. It is also not documented. I plan to add some examples to show basic usage.

Note that circuit-based implementations are generally slower and this framework is more targeting research on practical circuit obfuscation for cryptographic purposes. It is well suited for proof-of-concept implementations, for example to be submitted to the [WhibOx 2019](https://whibox.cyber-crypt.com/) competition (see also [WhibOx 2017](https://whibox-contest.github.io/)).

**Requirements**: Python2, [SageMath](http://www.sagemath.org/), [PyPy2](https://pypy.org/) (recommended). Python 3 support may be added soon.

Run `$ make` to compile a C library for fast simulation.

## Workflow example

### 1. Minimal Example for Masked AES

The following code creates AES circuit with *configurable* masking (quadratic MINQ + linear DOM-indep). The masking uses pseudorandomness generated from the plaintext using an LFSR initialised after two-round AES. It is also pooled to save on pseudorandomness generation as it is quite expensive.

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
```

Next, the circuit is compiled to a standalone C code that can be submitted to the WhibOx competition (if it fits the resource limitations of course). It uses a default method to encode and simulate the circuit.

```python
from whitebox.whibox import whibox_generate
whibox_generate(ct, "build/submit.c", "Hello, world!")
```

For local analysis and attacks the circuit can be serialized in a compact binary format to a file.

```python
from whitebox.serialize import RawSerializer
RawSerializer().serialize_to_file(ct, "circuits/aes10.bin")
```

This is example is placed in [./examples/minimal.py](). It can be run straightforwardly as follows. You can at first comment lines with masking first to make the generation faster and to see how attacks can recover the key.

```bash
$ pypy examples/minimal.py
```

### 2. Tracing the Circuit

Serialized circuit can be simulated by fast C simulator available from Python API. It is especially efficient in batch mode, where 64 inputs can be processed in one run (assuming 64-bit architecture).

```python
from whitebox.fastcircuit import FastCircuit
C = FastCircuit("circuits/aes10.bin")
ciphertext = C.compute_one("my_plaintext_abc")
ciphertexts = C.compute_batch(["my_plaintext_abc", "anotherPlaintext"])
```

For DCA-style attacks, we need to collect traces of the values computed in the circuit. The `FastCircuit` class supports tracing. For this we only need to specify filename to save the trace.

```python
import os
from whitebox.utils import chunks
plaintexts = os.urandom(16 * 128) # 128 traces
ciptertexts = C.compute_batches(
    inputs=chunks(plaintexts, 16),
    trace_filename_format="./traces/mytrace.%d"
)
```

The trace files contain compactly packed data, 64 encryptions per file. Each 8-byte block in a file corresponds to 64 bits recorded in one node of the circuit for all 64 different encryptions. We can further split such file into 64 separate files, one trace per encryption.

```python
from whitebox.tracing import trace_split_batch

trace_split_batch(
    filename="./traces/mytrace.0",
    make_output_filename=lambda j: "./traces/%04d.bin" % j,
    ntraces=64,
    packed=True
)
```

To simplify this procedure, a simple tool is available in [./tools/trace.py](). For example, 128 traces can be generated as follows:

```bash
$ pypy tools/trace.py circuits/aes10.bin 128
```

It generates traces to files of the form `./traces/0000.bin`. The corresponding plaintext and ciphertext are placed respectively in `./traces/0000.pt` and `./traces/0000.ct`.

### 3. DCA-Style Attacks

This framework includes 3 attacks based on analyzing the traces. The common idea is to guess a byte of the key in the first round of AES, to compute an S-Box over all plaintexts, and to "trace" an output bit (or a linear combination) of the S-Box. Then the attacks attempt to find a relation between this "predicted" vector with vectors from the trace.

1. The first attack tries to find an exact version of the vector. It is very fast by applies only to unprotected versions of AES. It also includes a second-order variant which searches for a pair of vectors that XOR to a predicted vector. It can break AES protected with a first-order linear masking scheme.

    The switch between first-order and the second-order attack is currently inside the script, along with many other configuration options. It can be ran as follows, to run the attack on the first 128 traces with a sliding window of 10000 nodes and step 2500.

```bash
$ pypy attacks/analyze_exact.py 128 10000 2500
```

2. The second attack tries to correlate each vector from the trace to a predicted vector. For this purpose we use the amazing tool [Daredevil](https://github.com/SideChannelMarvels/Daredevil) from the [SideChannelMarvels](https://github.com/SideChannelMarvels) collection. We only need to transform the traces to the right format and to generate a config file for it. The config can be modified after generation or right in the script [./attacks/combine4daredevil.py]().

```bash
$ pypy attacks/combine4daredevil.py 128
$ daredevil -c daredevil.config
```

3. The third attack tries to find a linear combination of vectors from traces that XOR to a predicted vector (in a reasonably sized window). It breaks any order of linear masking, if all the shares indeed are contained in the analyzed window.

    It has to be run with [SageMath](http://www.sagemath.org/). The following example runs it on 128 traces with window of 100 nodes and window step 25. Note that in order to avoid false positives, the number of traces should be larger than the window size by a constant amount.

```bash
$ sage attacks/analyze_linalg_1st.py 128 100 25
```

See the brief  summary on the masking schemes and applicable attacks:

[](./attacks_summary.png)

Note that fault attacks are not implemented yet in the framework and there are no protections against them as well.
