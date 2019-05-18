#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <time.h>

FILE *ftrace = NULL;

typedef unsigned char WORD;

WORD m[1<<$PLACE_MEMLOG];
int ct_pos[128] = {$CT_POSES};

int num_opcodes = $NUM_OPCODES;

unsigned char opcodes[$OPCODES_SIZE] = {};

unsigned char randbit() {
  return rand() & 1;
}

void compute() {
    unsigned char *p = (void*)opcodes;
    for(int i = 0; i < num_opcodes; i++) {
        unsigned char op = *p++;
        // printf("%d: %d\n", i, op);
        unsigned short dst = *((unsigned short *)p); p+=2;
        if (op == 0) {
            unsigned short a = *((unsigned short *)p); p+=2;
            unsigned short b = *((unsigned short *)p); p+=2;
            m[dst] = m[a] ^ m[b];
        }
        else if (op == 1) {
            unsigned short a = *((unsigned short *)p); p+=2;
            unsigned short b = *((unsigned short *)p); p+=2;
            m[dst] = m[a] & m[b];
        }
        else if (op == 2) {
            unsigned short a = *((unsigned short *)p); p+=2;
            m[dst] = ((WORD)-1) ^ m[a];
        }
        else if (op == 3) {
            m[dst] = randbit();
        }
        else {
            printf("unknown opcode %d\n", op);
            exit(0);
        }

        if (ftrace) {
            m[dst] &= 1;
            fwrite(m+dst, 1, 1, ftrace);
        }
    }
}

void AES_128_encrypt(char*ct, char*pt) {
    for(int i = 0; i < 128; i++) {
        m[i] = (pt[i/8] >> (7 - i % 8)) & 1;
    }

    compute();

    for(int i = 0; i < 16; i++) {
        ct[i] = 0;
    }
    for(int i = 0; i < 128; i++) {
        ct[i/8] |= (m[ct_pos[i]]&1) << (7 - i % 8);
    }
    return;
}

int main() {
    int tmp;

    // CSPRNG?..
    srand(time(NULL));
    srand(rand() ^ getpid());

    if (getenv("DISABLE_RANDOM") && atoi(getenv("DISABLE_RANDOM")))
        srand(4294967291);

    char *trace_fname = getenv("TRACE");
    if (trace_fname) {
        ftrace = fopen(trace_fname, "w");
        assert(ftrace);
    }

    char *opcodes_fname = getenv("OPCODES");
    assert(opcodes_fname);
    FILE * fd = fopen(opcodes_fname, "r");
    assert(fd);
    assert(sizeof(opcodes) == fread(opcodes, 1, sizeof(opcodes), fd));
    fclose(fd);

    char plaintext[16];
    char ciphertext[16];
    while (fread(plaintext, 1, 16, stdin) == 16) {
        AES_128_encrypt(ciphertext, plaintext);
        fwrite(ciphertext, 1, 16, stdout);
    }
    return 0;
}
