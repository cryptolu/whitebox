#!/bin/bash -e

NTRACES=$1
WINDOW=$2
PYTHON=$(which pypy || which python2 || which python)

"$PYTHON" analyze_exact.py "$NTRACES" "$WINDOW"
