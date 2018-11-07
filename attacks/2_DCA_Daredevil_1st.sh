#!/bin/bash -e

NTRACES=$1
PYTHON=$(which pypy || which python2 || which python)

echo Combining traces for Daredevil...
"$PYTHON" combine4daredevil.py "$NTRACES"

echo Running Daredevil
daredevil -c daredevil.config
