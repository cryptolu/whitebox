#!/usr/bin/env sage
from sage.all import *

FNAME = sys.argv[1]
FINAME = sys.argv[1] + ".names"

order = "Cxyrv"
traces = {}
inputs = []
nodes = []
ntraces = None

for line in open(FNAME):
	parts = line.strip().split("`")
	if not parts:
		continue
	name, vec = parts
	traces[name] = map(int, vec)
	if not name.startswith("v"):
		inputs.append(name)
	nodes.append(name)
	if ntraces is None:
		ntraces = len(vec)
	assert ntraces == len(vec)
assert ntraces & (ntraces - 1) == 0, "number of traces must be a power of 2"

infos = {"C": "const1"}
for line in open(FINAME):
	parts = line.strip().split("`")
	if not parts:
		continue
	name, info = parts
	infos[name] = info

# constant vector
inputs = ["C"] + inputs
nodes = ["C"] + nodes
traces["C"] = (1,) * ntraces

inputs.sort(key=lambda name: order.index(name[0]))

nmain = sum(1 for name in inputs if name[0] in "Cxy")
nrand = len(inputs) - nmain

main_inputs = inputs[:nmain]
rand_inputs = inputs[nmain:nmain+nrand]

print "Verifying 1-st order algebraic security"
print "main inputs", " ".join(main_inputs)
print "rand inputs", " ".join(rand_inputs)
print " all inputs", " ".join(inputs)
print "  all nodes", " ".join(nodes)
print

print "INPUTS"
mx = matrix(GF(2), ntraces, len(main_inputs))
num1 = mx.ncols()
for x, node in enumerate(main_inputs):
	mx.set_column(x, traces[node])
num2 = mx.column_space().dimension()

print "- reduction:", num1, "->", num2
print
assert num1 == num2, "inputs must be linearly independent"

print "NODES"
m0 = m = matrix(GF(2), ntraces, len(nodes))
num1 = m.ncols()
for x, node in enumerate(nodes):
	m.set_column(x, traces[node])
num2 = m.ncols()
print "- reduction:", num1, "->", num2
print

if 1: # print basis vectors
	for x in xrange(m.ncols()):
		col = m.column(x)
		sol = m0.solve_right(col)
		print "- nodes basis vector %3d:" % x, " + ".join(name for name, v in zip(nodes, sol) if v)
		# for name, v in zip(nodes, sol):
		# 	if v:
		# 		print "---", name, infos[name]
	print

mrank = m.column_space().dimension()
mxrank = mx.column_space().dimension()

print "ZONES CHECK", mrank, mxrank
zone_size = 1 << nrand
for zone_index in xrange(ntraces >> nrand):
	sub  =  m[zone_index * zone_size : (zone_index + 1) * zone_size]
	subx = mx[zone_index * zone_size : (zone_index + 1) * zone_size]

	m_nullity = mrank - sub.column_space().dimension()
	mx_nullity = mxrank - subx.column_space().dimension()
	print "- zone %3d:" % zone_index, m_nullity, mx_nullity, "(from sub dim %d %d)" % (sub.column_space().dimension(), subx.column_space().dimension())
	assert m_nullity == mx_nullity, "nullity must be equal (insecure!)"

print "------------------------------------------------"
print "VERDICT: Gadget is 1-th order algebraically secure"
print "------------------------------------------------"
