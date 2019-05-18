# Verification of Circuit Algebraic Security

This folder contains an implementation of the **Algorithm 2** from the paper. It checks whether a small circuit (a gadget) is *algebraically secure*.

### How to run:

1. Define the target circuit in the file `gadget_trace.py`. The minimalist masking scheme from the paper is included and chosen by default. The circuit is defined using symbolic computations, see `minimalist3.py` for an example.
2. Run `./gadget_trace.py` with Python2/PyPy2. It reports **the maximum degree** and **the bias bound**. It also generates a "trace" taken on all possible inputs, i.e. truth tables of all computed functions.
3. Run `./gadget_check.py` with Sage and specify path to the trace file as an argument. It implements **Algorithm 2** from the paper. The algorithm checks whether the circuit is *1-AS-secure* or not.

### Example:

```
$ sage gadget_trace.py
<Scheme minimalist3 N=3 NR=3>

4 = x0 : x0
5 = x1 : x1
6 = x2 : x2
7 = y0 : y0
8 = y1 : y1
9 = y2 : y2
10 = rx0 : rx0
11 = rx1 : rx1
12 = rx2 : rx2
13 = ry0 : ry0
14 = ry1 : ry1
15 = ry2 : ry2
18 = AND 10 17 : degree on r 2, full 2: rx0*rx2 ^ rx0*x1
19 = AND 11 16 : degree on r 2, full 2: rx1*rx2 ^ rx1*x0
23 = AND 21 22 : degree on r 2, full 2: rx0*rx1 ^ rx0*rx2 ^ rx1*rx2 ^ rx2
31 = AND 13 30 : degree on r 2, full 2: ry0*ry2 ^ ry0*y1
32 = AND 14 29 : degree on r 2, full 2: ry1*ry2 ^ ry1*y0
36 = AND 34 35 : degree on r 2, full 2: ry0*ry1 ^ ry0*ry2 ^ ry1*ry2 ^ ry2
42 = AND 26 40 : degree on r 2, full 2: rx0*ry1 ^ rx0*y1 ^ ry1*x0 ^ x0*y1
43 = AND 27 39 : degree on r 2, full 2: rx1*ry0 ^ rx1*y0 ^ ry0*x1 ^ x1*y0
52 = AND 10 51 : degree on r 2, full 2: rx0*rx2 ^ rx0*x1
53 = AND 11 50 : degree on r 2, full 2: rx1*rx2 ^ rx1*x0
57 = AND 55 56 : degree on r 2, full 2: rx0*rx1 ^ rx0*rx2 ^ rx1*rx2 ^ rx2
65 = AND 13 64 : degree on r 2, full 2: ry0*ry2 ^ ry0*y1
66 = AND 14 63 : degree on r 2, full 2: ry1*ry2 ^ ry1*y0
70 = AND 68 69 : degree on r 2, full 2: ry0*ry1 ^ ry0*ry2 ^ ry1*ry2 ^ ry2
76 = AND 60 74 : degree on r 2, full 2: rx0*ry1 ^ rx0*y1 ^ ry1*x0 ^ x0*y1
78 = AND 61 73 : degree on r 2, full 2: rx1*ry0 ^ rx1*y0 ^ ry0*x1 ^ x1*y0
80 = AND 62 74 : degree on r 3, full 3: rx0*rx1*ry1 ^ rx0*rx1*y1 ^ rx0*ry1*x1 ^ rx0*x1*y1 ^ rx1*ry1*x0 ^ rx1*x0*y1 ^ ry1*x2 ^ x2*y1
81 = AND 61 15 : degree on r 2, full 2: rx1*ry2 ^ ry2*x1
83 = AND 82 73 : degree on r 4, full 4: rx0*rx1*ry0*ry1 ^ rx0*rx1*ry0*y1 ^ rx0*rx1*ry1*y0 ^ rx0*rx1*y0*y1 ^ rx0*ry0*ry1*x1 ^ rx0*ry0*x1*y1 ^ rx0*ry1*x1*y0 ^ rx0*x1*y0*y1 ^ rx1*ry0*ry1*x0 ^ rx1*ry0*ry2 ^ rx1*ry0*x0*y1 ^ rx1*ry1*x0*y0 ^ rx1*ry2*y0 ^ rx1*x0*y0*y1 ^ ry0*ry1*x2 ^ ry0*ry2*x1 ^ ry0*x2*y1 ^ ry1*x2*y0 ^ ry2*x1*y0 ^ x2*y0*y1
84 = AND 61 75 : degree on r 3, full 3: rx1*ry0*ry1 ^ rx1*ry0*y1 ^ rx1*ry1*y0 ^ rx1*y2 ^ ry0*ry1*x1 ^ ry0*x1*y1 ^ ry1*x1*y0 ^ x1*y2
85 = AND 74 12 : degree on r 2, full 2: rx2*ry1 ^ rx2*y1
87 = AND 86 60 : degree on r 4, full 4: rx0*rx1*ry0*ry1 ^ rx0*rx1*ry0*y1 ^ rx0*rx1*ry1*y0 ^ rx0*rx1*y2 ^ rx0*rx2*ry1 ^ rx0*rx2*y1 ^ rx0*ry0*ry1*x1 ^ rx0*ry0*x1*y1 ^ rx0*ry1*x1*y0 ^ rx0*x1*y2 ^ rx1*ry0*ry1*x0 ^ rx1*ry0*x0*y1 ^ rx1*ry1*x0*y0 ^ rx1*x0*y2 ^ rx2*ry1*x0 ^ rx2*x0*y1 ^ ry0*ry1*x0*x1 ^ ry0*x0*x1*y1 ^ ry1*x0*x1*y0 ^ x0*x1*y2
88 = AND 62 75 : degree on r 4, full 4: rx0*rx1*ry0*ry1 ^ rx0*rx1*ry0*y1 ^ rx0*rx1*ry1*y0 ^ rx0*rx1*y2 ^ rx0*ry0*ry1*x1 ^ rx0*ry0*x1*y1 ^ rx0*ry1*x1*y0 ^ rx0*x1*y2 ^ rx1*ry0*ry1*x0 ^ rx1*ry0*x0*y1 ^ rx1*ry1*x0*y0 ^ rx1*x0*y2 ^ ry0*ry1*x2 ^ ry0*x2*y1 ^ ry1*x2*y0 ^ x2*y2
89 = AND 15 12 : degree on r 2, full 2: rx2*ry2

------------------------------------------
Maximum degree: 4
Bias bound: bias <= 7/16
Provable security:
 80 bit: R > 939
128 bit: R > 1502
------------------------------------------

Traces written

$ sage gadget_check.py traces/minimalist3
Verifying 1-st order algebraic security
main inputs C x0 x1 x2 y0 y1 y2
rand inputs rx0 rx1 rx2 ry0 ry1 ry2
 all inputs C x0 x1 x2 y0 y1 y2 rx0 rx1 rx2 ry0 ry1 ry2
  all nodes C x0 x1 x2 y0 y1 y2 rx0 rx1 rx2 ry0 ry1 ry2 v0 v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 v19 v20 v21 v22 v23

INPUTS
- reduction: 7 -> 7

NODES
- reduction: 37 -> 37

...

------------------------------------------------
VERDICT: Gadget is 1-th order algebraically secure
------------------------------------------------

```
