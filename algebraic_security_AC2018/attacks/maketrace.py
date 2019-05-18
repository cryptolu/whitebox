#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import sys, os
from subprocess import check_output

program = sys.argv[1]
n = int(sys.argv[2])

pts = []
cts = []

for i in xrange(n):
    print "Trace", i
    fpt = "traces/%04d.pt" % i
    fct = "traces/%04d.ct" % i
    ft = "traces/%04d.bin" % i

    if not os.path.exists(fpt):
        print "   ", "new plaintext"
        pt = os.urandom(16)
        with open(fpt, "w") as f: f.write(pt)
    with open(fpt) as f: pt = f.read(16)

    os.environ["TRACE"] = ft
    ct = check_output([program], stdin=open(fpt))
    with open(fct, "w") as f: f.write(ct)
    print "   ", "size", os.stat(ft).st_size
