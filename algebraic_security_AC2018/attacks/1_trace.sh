#!/bin/bash -e

NTRACES=$1
PYTHON=$(which pypy || which python2 || which python)

echo Cleaning traces...
rm -f traces/*.{pt,ct,bin,input,output}

echo Tracing...
export OPCODES=../implementation/build/opcodes.bin
"$PYTHON" maketrace.py ../implementation/build/code.bin "$NTRACES"
