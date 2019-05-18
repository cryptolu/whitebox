#!/bin/bash -e

rm -f build/code.bin || true

CC=$(which tcc || which gcc || which clang)
"$CC" build/code.c -o build/code.bin

export OPCODES=./build/opcodes.bin

>./build/ciphertext.bin

echo "Encrypting..."
time ./build/code.bin <test_plaintext >./build/ciphertext.bin
echo

echo "Ciphertext:"
xxd ./build/ciphertext.bin
echo

echo "Difference:"
diff <(xxd ./build/ciphertext.bin) <(xxd test_ciphertext)

echo ==========
