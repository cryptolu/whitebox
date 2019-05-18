/*
$comment
*/
typedef unsigned char W;
typedef unsigned short A;
typedef unsigned char B;

enum OP {_, XOR, AND, OR, NOT, RANDOM};

A input_addr[] = {$input_addr};
A output_addr[] = {$output_addr};
B opcodes[] = $opcodes_encoded;
W ram[$ram_size];

void AES_128_encrypt(char *ct, char *pt) {
    for (int i = 0; i < 128; i++) {
        ram[input_addr[i]] = (pt[i>>3]>>(7-i&7)) & 1;
    }

    #define pop() p+=sizeof(A)
    B *p = opcodes;
    for(int i = 0; i < $num_opcodes; i++) {
        B op = *p++;
        A dst = *((A *)p); pop();
        A a, b;
        switch (op) {
        case XOR:
            a = *((A *)p); pop();
            b = *((A *)p); pop();
            ram[dst] = ram[a] ^ ram[b];
            break;
        case AND:
            a = *((A *)p); pop();
            b = *((A *)p); pop();
            ram[dst] = ram[a] & ram[b];
            break;
        case OR:
            a = *((A *)p); pop();
            b = *((A *)p); pop();
            ram[dst] = ram[a] | ram[b];
            break;
        case NOT:
            a = *((A *)p); pop();
            ram[dst] = 1^ram[a];
            break;
        case RANDOM:
            ram[dst] = 0; // not useful for contest (or implement your rand and obfuscate...)
            break;
        default:
            return; // ouch?
        }
    }

    for (int i = 0; i < 128; i++) {
        if (!(i&7)) ct[i>>3] = 0;
        ct[i>>3] |= (ram[output_addr[i]]&1) << (7-i&7);
    }
}
