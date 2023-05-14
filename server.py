import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5000))
server.listen()

clients = []
nicknames = []
publicKeys = []

#broadcast
def broadcast(message, publicKey) :
    for client in clients :
        concat = f"{message.decode('utf-8')}\n\nMESSAGE{publicKey[0].decode('utf-8')}\n\n{publicKey[1].decode('utf-8')}"
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

        publicKeys.append((publicKey1, publicKey2))
        nicknames.append(nickname)
        clients.append(client)

        broadcast(f"{nickname} connected to server".encode('utf-8'), (publicKey1, publicKey2))
        client.send("Connected to the server".encode('utf-8'))


        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server Running")
receive()
































# server.listen()

# client, addr = server.accept()

# isFinish = False

# while not isFinish :
#     message = client.recv(1024).decode('utf-8')
#     if(message == 'quit'):
#         isFinish = True
#     else :
#         print("Client : ", message)
#     client.send(input("You :").encode('utf-8'))