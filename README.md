# White-box Algebraic Security

This repository contains proof-of-concept code for the paper

- [Attacks and Countermeasures for White-box Designs](https://eprint.iacr.org/2018/049) \
by Alex Biryukov and Aleksei Udovenko ([ASIACRYPT 2018](https://www.springer.com/gp/book/9783319706931))

The code is splitted into three parts:

1. **Implementation**: Proof-of-concept implementation of AES using the new nonlinear masking scheme.
1. **Verification**: Code for verifying algebraic security of gadgets.
1. **Attacks**: Several attacks from the paper.

**Requirements**: Python2, [SageMath](http://www.sagemath.org/), [PyPy2](https://pypy.org/) (recommended)
