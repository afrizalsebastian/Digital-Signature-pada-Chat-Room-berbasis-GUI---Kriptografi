import math
import sys
from typing import List

# Round Constant
RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
      0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
      0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
      0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
      0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
      0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
      0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
      0x8000000000008080, 0x0000000080000001, 0x8000000080008008]

ROT_OFFSET = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14]
]

def printBytesInList(val : bytes):
    list = []
    for x in val:
        list.append(x)
    print(list)

def Keccak(message : str, ):
    # SHA3-256
    digest = 256
    r = 1088
    c = 512
    w = 360 # bisa dipilih sebebasnya, tapi pada keccak pada umumnya64
    # Padding
    Mbits = bin(int.from_bytes(message.encode(), byteorder='little'))[2:]
    Mbytes = message.encode()
    
    
    d = 2 ** len(Mbits) + sum([2**i * int(Mbits[i]) for i in range(len(Mbits))]) # kalau index ke i mulai dari depan
    P = Mbytes + d.to_bytes((d.bit_length() + 7) // 8, 'little')
    
    P = P + bytes((r//8) * math.ceil(len(P)/(r//8)) - len(P)) # Beri padding 0 sehingga P berukuran kelipatan r
    P = P[:len(P)-1] + bytes([P[len(P)-1] ^ 0x80]) # ini udah benarkah meletakkan \x80 di akhir (atau di depan?)

    # Initialization
    S = [[0 for i in range(5)] for j in range(5)]

    # Memecah (P message + padding) menjadi block berukuran r    
    P_blocks = []
    idxStartBlock = 0
    while idxStartBlock < len(P):
        P_blocks.append(P[idxStartBlock:idxStartBlock+(r//8)]) # totalnya 136 hex sesuai dengan r 136*8bit = 1088 bit
        idxStartBlock += r//8

    # Absorbing Phase
    for P_block in P_blocks:
        idxStartP_block = 0
        countFlatten = 0
        i = 0
        while (i < len(S) and countFlatten < len(P_block)//8): 
            j = 0
            while (j < len(S[0]) and countFlatten < len(P_block)//8): 
                if (i+5*j < r/w):
                    S[i][j] = S[i][j] ^ int.from_bytes(P_block[idxStartP_block:idxStartP_block+8], 'little')
                j += 1
                countFlatten += 1
                idxStartP_block += 8
                
            i += 1

        # Masuk ke round function f
        S = KeccakPermutation(S,r+c)
    Z = b""
    countFlatten = 0
    count = 0
    while (len(Z) < (digest//8)):
        i = 0
        while (i < len(S) and countFlatten < (r//8)//8 and len(Z) < (digest//8)):

            j = 0
            while (j < len(S[0]) and countFlatten < (r//8)//8 and len(Z) < (digest//8)):
                if (i+5*j < r/w):
                    count+=1

                    Z += S[i][j].to_bytes((S[i][j].bit_length() + 7) // 8, 'little')

                countFlatten += 1
                j+=1
            i+=1
            
        S = KeccakPermutation(S,r+c)
    return Z

def KeccakPermutation(A : List[List[int]], b:int):
    n = 12 + 2 * int(math.log2(b / 25))
    for i in range(n):
        A = KeccakRound(A, RC[i], b)
    return A

def KeccakRound(A : List[List[int]], RCnow, b:int):
    # tetha step
    C = []
    for i in range(len(A)):
        C.append(A[i][0] ^ A[i][1] ^ A[i][2] ^ A[i][3]^ A[i][3])
    D = []
    for i in range(len(A)):
        D.append((C[(i-1)%5] ^ rot(C[(i+1)%5],1)) % (1 << 64))
    
    for i in range(len(A)):
        for j in range(len(A[0])):
            A[i][j] = A[i][j] ^ D[i]
    
    # rho and phi Steps
    B = [[0 for y in range(len(A[0]))] for x in range(len(A))]
    for i in range(len(A)):
        for j in range(len(A[0])):
            B[j][(2 * i + 3 * j) % 5] = rot(A[i][j], ROT_OFFSET[i][j])

    # chi step
    for i in range(len(A)):
        for j in range(len(A[0])):
            A[i][j] = B[i][j] ^ (~B[(i+1)%5][j] & B[(i+2)%5][j]) 

    # iota step
    A[0][0] ^= RCnow

    return A

def rot(x, y):
    return ((x << y) | (x >> (64 - y))) % (1 << 64)
