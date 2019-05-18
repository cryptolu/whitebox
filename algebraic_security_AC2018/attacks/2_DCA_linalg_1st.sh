#!/bin/bash -e

NTRACES=$1
WINDOW=$2

sage analyze_linalg_1st.py "$NTRACES" "$WINDOW"
