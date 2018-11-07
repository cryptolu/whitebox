# Attacks on White-box implementations

This folder contains several attacks on white-box implementations.

### How to run:

1. Run `./0_build.sh` to compile the implementation in the ../implementation folder (possibly using DISABLE_NONLINEAR_MASKING=1 flag).
2. Run `./1_trace.sh 200`\
(200 is the number of traces)
3. Run one of the attack scripts (starting with 2_), e.g. `./2_DCA_linalg_1st.sh 200 100`\
(200 is the number of traces, 100 is the window size).

The default key in the implementation is **"samplekey1234567"**, which in hex is

`73 61 6d 70 6c 65 6b 65 79 31 32 33 34 35 36 37`

Set environment variable `DISABLE_RANDOM=1` **during traces generation** to disable randomness in the AC18 implementation.

Set environment variable `DISABLE_NONLINEAR_MASKING=1` **during compilation** to disable the quadratic masking scheme.

The `1_trace.sh` script generates value traces of the implementation. They are saved in the `traces/` folder, e.g. `traces/0001.pt`, `traces/0001.ct`, `traces/0001.bin`. The latter file contains the recorded values, one bit per byte (uncompressed). The traces are used further by the attacks.

Note that in these attack implementations windows are chosen using a sliding window on the trace file. A more advanced strategy would be to generate window coverage based on the circuit based on distances in the circuit graph.


## First-order linear algebra attack

**Script:** 2_DCA_linalg_1st.sh\
**Code and configuration:** analyze_linalg_1st.py\
**Requirements:** [SageMath](http://www.sagemath.org/)

An implementation of the 1-st order linear algebra attack in [Sage](http://www.sagemath.org/).

The implementation with `DISABLE_NONLINEAR_MASKING=1` can be broken using this attack (or if `DISABLE_RANDOM=1` is set and the masking scheme becomes ineffective). Otherwise, the implementation is secure against this attack.

```
$ DISABLE_NONLINEAR_MASKING=1 ./0_build.sh
$ ./1_trace.sh 200
$ ./2_DCA_linalg_1st.sh 200 100
... (time ~5 seconds)
Window 30 / 4050 offset 725-824
    100 vectors
    100 unique vectors
    1536 target vectors
MATCH: sbox #0, lin.mask 0x01, key 0x73='s', negated? True, indexes 733...823 (distance 90) [733, 734, 735, 739, 745, 757, 759, 761, 763, 767, 772, 783, 818, 822, 823]

$ DISABLE_NONLINEAR_MASKING=0 ./0_build.sh
$ ./1_trace.sh 200
$ ./2_DCA_linalg_1st.sh 200 100
... (time ~4 hours)
No matches.
```

## Time-memory trade-off attack on linear masking

**Script:** 2_DCA_exact_1st_2nd.sh\
**Code and configuration:** analyze_exact.py

An implementation of the time-memory trade-off attack. The first-order attack searches for exact match of the predicted value in the traces (breaks unprotected implementations). The second order attack searches for a pair of shares that exactly match the predicted value (breaks first-order masked implementation).

The implementation with `DISABLE_NONLINEAR_MASKING=1` can be broken with the second order attack. If `DISABLE_RANDOM=1` is set, then the masking schemes become ineffective and even the first order attack recovers the key. Without these options this attack is ineffective.


## First-order correlation attack (using Daredevil)

**Script:** 2_DCA_Daredevil_1st.sh\
**Requirements:** [Daredevil](https://github.com/SideChannelMarvels/Daredevil)

Here the implementation is tested using the [Daredevil tool]( https://github.com/SideChannelMarvels/Daredevil). The traces are collected and Daredevil attempts the first-order correlation attack. As the implementation is first-order protected by a linear masking scheme, the key is not recovered. However, the key can be recovered by disabling the randomness in the implementation. If `DISABLE_RANDOM` is set to 1, then the key can be recovered with just a few traces, e.g. 20. Note that the quadratic masking scheme by itself does not prevent this attack.

The config file `daredevil.conf` is generated and can be modified and reused. For example, to run the second-order attack.
