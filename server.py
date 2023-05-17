import socket
import threading
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5000))
server.listen()

clients = []
nicknames = []
publicKeys = []
encryptKey = get_random_bytes(32)
cipher = AES.new(encryptKey, AES.MODE_ECB)

def pad_data(data:bytes):
    padding_length = 16 - (len(data) % 16)
    padding = chr(padding_length) * padding_length
    return data + padding.encode()

#broadcast
def broadcast(message, publicKey) :
    for client in clients :
        concat = f"{message}\n\nMESSAGE{publicKey[0].decode('utf-8')}\n\n{publicKey[1].decode('utf-8')}"
        client.send(concat.encode('utf-8'))

def handle(client):
    while True :
        try :
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]} says {message}")
            index = clients.index(client)
            publicKey = publicKeys[index]
            broadcast(message, publicKey)
        except :
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            publicKey = publicKeys[index]
            publicKeys.remove(publicKey)
            break

#receive
def receive():
    while True :
        client, address = server.accept()
        print(f"connected with {str(address)}")
        client.send("PUBLIC-1".encode('utf-8'))
        publicKey1 = client.recv(2048)

        client.send("PUBLIC-2".encode('utf-8'))
        publicKey2 = client.recv(2048)
        
        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024)

        client.send(f"ENCKEY\n{encryptKey}".encode('utf-8'))

        publicKeys.append((publicKey1, publicKey2))
        nicknames.append(nickname)
        clients.append(client)

        broadcast(cipher.encrypt(pad_data(f"{nickname.decode('utf-8')} connected to chat room\n".encode('utf-8'))), (publicKey1, publicKey2))
        # client.send(cipher.encrypt(pad_data(f"Connected to the server\n".encode('utf-8'))))


        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server Running")
receive()