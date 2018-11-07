#!/bin/bash -e

PYTHON=$(which pypy || which python2 || which python)

(cd ../implementation/ && "$PYTHON" generate.py && ./buildrun.sh)
