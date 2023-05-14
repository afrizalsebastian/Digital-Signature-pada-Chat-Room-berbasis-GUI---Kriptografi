# Elliptic Curve Digital Signature Algorithm (ECDSA)
import random
from Keccak import Keccak

class ECDSA:
    def __init__(self):
        # ECDSA parameters
        self.p = pow(2, 255) - 19
        self.B = [
                15112221349535400772501151409588531511454012693041857206046113283949847762202, 
                46316835694926478169428394003475163141307993866256225615783033603165251855960
            ]
        self.a = -1
        self.d = self.modulus(-121665 * self.invModulus(121666, self.p), self.p)
    
    def gcd(self, a, b):
        while a != 0:
            a, b = b % a, a
        return b

    def strToInt(self, string):
        encoded = string.encode('utf-8')
        hex_rep = encoded.hex()
        int_rep = int(hex_rep, 16)
        return int_rep

    def modulus(self, a, b):
        if a < 0:
            a = (a + b * int(abs(a)/b) + b) % b
        return a

    def invModulus(self, a, b):
        if a < 0:               # a negatif
            a = (a + b * int(abs(a)/b) + b) % b
        if self.gcd(a, b) != 1:      # a dan b relatif prima
            return None
        # Extended Euclidean Algorithm:
        x1, y1, z1 = 1, 0, a
        x2, y2, z2 = 0, 1, b
        while z2 != 0:
            q = z1 // z2
            x1, y1, z1, x2, y2, z2 = x2, y2, z2, x1 - q * x2, y1 - q * y2, z1 - q * z2
        return x1 % b

    def pointAdd(self, P, Q, a, d, mod):
        x1 = P[0]
        y1 = P[1]
        x2 = Q[0]
        y2 = Q[1]
        x3 = (((x1 * y2 + y1 * x2) % mod) * self.invModulus(1 + d * x1 * x2 * y1 * y2, mod)) % mod
        y3 = (((y1 * y2 - a * x1 * x2) % mod) * self.invModulus(1 - d * x1 * x2 * y1 * y2, mod)) % mod
        return x3, y3

    def pointMultiply(self, P, k, a, d, mod):
        result = (P[0], P[1])
        kBytes = bin(k)[2 : len(bin(k))]  # convert to binary and remove 0b prefix
        for i in range(1, len(kBytes)):
            currentBit = kBytes[i: i+1]
            result = self.pointAdd(result, result, a, d, mod)
            if currentBit == '1':
                result = self.pointAdd(result, P, a, d, mod)
        return result

    def generateKeyPair(self):
        privateKey = random.getrandbits(256) #32 byte secret key
        publicKey = self.getPublicKey(privateKey)
        return privateKey, publicKey
    
    def getPublicKey(self, privateKey):
        return self.pointMultiply(self.B, privateKey, self.a, self.d, self.p)

    def hashing(self, message):
        messageStr = str(message)
        return int.from_bytes(Keccak(messageStr), byteorder='big')

    def sign(self, message, privateKey):
        publicKey = self.getPublicKey(privateKey)
        r = self.hashing(self.hashing(message) + message) % self.p
        R = self.pointMultiply(self.B, r, self.a, self.d, self.p)
        h = self.hashing(R[0] + publicKey[0] + message) % self.p
        s = (r + h * privateKey)
        return R, s
    
    def verify(self, message, publicKey, signature):
        R = signature[0]
        s = signature[1]
        h = self.hashing(R[0] + publicKey[0] + message) % self.p
        P1 = self.pointMultiply(self.B, s, self.a, self.d, self.p)
        P2 = self.pointAdd(R, self.pointMultiply(publicKey, h, self.a, self.d, self.p), self.a, self.d, self.p)
        if P1[0] == P2[0] and P1[1] == P2[1]:
            return True
        else:
            return False
    
    def getECCCurve(self):
        return "curve (ed25519): ",self.a,"x^2 + y^2 = 1 + ",self.d,"x^2 y^2"