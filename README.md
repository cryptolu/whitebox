# White-box Analysis and Implementation Tools

This repository contains various tools for (crypt)analysis and implementation of white-box designs. Currently, it has two major parts.


## [White-box Algebraic Security](./algebraic_security_AC2018)
This folder contains proof-of-concept code for the paper

[Attacks and Countermeasures for White-box Designs](https://eprint.iacr.org/2018/049) \
by Alex Biryukov and Aleksei Udovenko ([ASIACRYPT 2018](https://www.springer.com/gp/book/9783030033286))

The code is splitted into three parts:

1. **Implementation**: Proof-of-concept implementation of AES using the new nonlinear masking scheme.
1. **Verification**: Code for verifying algebraic security of gadgets.
1. **Attacks**: Several attacks from the paper.

[Slides](./algebraic_security_AC2018/slides.pdf) from the ASIACRYPT presentation are available.

[Paper](./algebraic_security_AC2018/WhiteBoxAttacksCountermeasures.pdf) is available.

**Requirements**: Python2, [SageMath](http://www.sagemath.org/), [PyPy2](https://pypy.org/) (recommended)

```
@inproceedings{AC18BU,
  author    = {Alex Biryukov and
               Aleksei Udovenko},
  title     = {Attacks and Countermeasures for White-box Designs},
  booktitle = {{ASIACRYPT} {(2)}},
  series    = {Lecture Notes in Computer Science},
  volume    = {11273},
  pages     = {373--402},
  publisher = {Springer},
  year      = {2018}
}
```

## [Synthesis Tools for White-box Implementations](./synthesis)

This repository contains a framework for implementing and analysing circuit-based implementations. It was presented at the [WhibOx 2019](https://www.cryptoexperts.com/whibox2019/) workshop by Aleksei Udovenko. It is basically a separated and improved version of the implementation framework used in the [White-box Algebraic Security](./algebraic_security_AC2018) part.

[Slides](./synthesis/slides.pdf) from the workshop are available.

**Requirements**: Python2, [SageMath](http://www.sagemath.org/), [PyPy2](https://pypy.org/) (recommended). Python 3 support may be added soon.

```
@misc{WB2019U,
  author    = {Aleksei Udovenko},
  title     = {Synthesis Tools for White-box Implementations},
  howpublished = {WhibOx 2019. White-Box Cryptography and Obfuscation (2nd Edition)},
  year      = {2019}
}
```
