from ECDSA import ECDSA

def sign(messages : str, privateKey : str):
    ecdsa = ECDSA()
    message = ecdsa.strToInt(messages)
    privateKey = int(privateKey)
    signature = ecdsa.sign(message, privateKey)
    signed_message = messages + "\n\nSIGNATURE_BEGIN\n" + hex(signature[0][0])[2:] + "\n" + hex(signature[0][1])[2:] + "\n" + hex(signature[1])[2:] + "\nSIGNATURE_END"
    return signed_message

def verify(signed_message : str, publicKey1 : str, publicKey2 : str):
    message = signed_message.split("\n\nSIGNATURE_BEGIN")[0]
    signature_string = signed_message.split("\n\nSIGNATURE_BEGIN")[1].split("\nSIGNATURE_END")[0].split("\n")
    signature = [[0, 0], 0]
    signature[0][0] = int(signature_string[1], 16)
    signature[0][1] = int(signature_string[2], 16)
    signature[1] = int(signature_string[3], 16)
    ecdsa = ECDSA()
    message = ecdsa.strToInt(message)
    publicKey1 = int(publicKey1)
    publicKey2 = int(publicKey2)
    publicKey = [publicKey1, publicKey2]
    valid = ecdsa.verify(message, publicKey, signature)
    return valid

def generateKeyPair():
    ecdsa = ECDSA()
    privateKey, publicKey = ecdsa.generateKeyPair()
    return privateKey, publicKey