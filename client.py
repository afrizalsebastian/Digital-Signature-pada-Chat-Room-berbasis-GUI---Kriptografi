import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from ECDSA import ECDSA
from Crypto.Cipher import AES

HOST = 'localhost'
PORT = 5000

class Client :
    
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)
        self.gui_done = False
        self.running = True
        self.setupCounter = 0
        self.privateKey, self.publicKey = self.generateKeyPair()

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.recieve)
        
        gui_thread.start()
        receive_thread.start()

    def generateKeyPair(self):
        ecdsa = ECDSA()
        privateKey, publicKey = ecdsa.generateKeyPair()
        return privateKey, publicKey


    def gui_loop(self) :
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")
        self.win.title("Digital Signature Chatroom")

        self.chat_label = tkinter.Label(self.win, text="Chatroom : ", bg="lightgray")
        self.chat_label.config(font=('Space Mono', 12))
        self.chat_label.pack(padx=15, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=15, pady=5)
        self.text_area.config(state='disabled', font=('Space Mono', 16),height=16)

        self.message_label = tkinter.Label(self.win, text="Message : ", bg="lightgray")
        self.message_label.config(font=('Space Mono', 12))
        self.message_label.pack(padx=15, pady=5)

        self.input_message = tkinter.Text(self.win, height=3)
        self.input_message.pack(padx=15, pady=5)

        self.send_button = tkinter.Button(self.win, text='Send', command=self.write)
        self.send_button.config(font=('Space Mono', 12))
        self.send_button.pack(padx=15, pady=5)

        self.nickname_label = tkinter.Label(self.win, text=f"Nickname : {self.nickname} ", bg="lightgray")
        self.nickname_label.config(font=('Space Mono', 16))
        self.nickname_label.pack(padx=15, pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def sign(self, messages : str, privateKey : str):
        ecdsa = ECDSA()
        message = ecdsa.strToInt(messages)
        privateKey = int(privateKey)
        signature = ecdsa.sign(message, privateKey)
        signed_message = messages + "\n\nSIGNATURE_BEGIN\n" + hex(signature[0][0])[2:] + "\n" + hex(signature[0][1])[2:] + "\n" + hex(signature[1])[2:] + "\nSIGNATURE_END"
        return signed_message
    
    def pad_data(self, data:bytes):
        padding_length = 16 - (len(data) % 16)
        padding = chr(padding_length) * padding_length
        return data + padding.encode()

    def write(self):
        message = f"{self.nickname} : {self.input_message.get('1.0', 'end')}"
        message = self.sign(message, self.privateKey)
        cipher = AES.new(self.encryptKey, AES.MODE_ECB)
        ciphertext = cipher.encrypt(self.pad_data(message.encode('utf-8')))
        self.socket.send(ciphertext)
        self.input_message.delete('1.0', 'end')
    
    def stop(self):
        self.running = False
        self.win.destroy()
        self.socket.close()
        exit(0)

        

    def verify(self, signed_message : str, publicKey1 : str, publicKey2 : str):
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
    
    def unpad_data(self, data : bytes):
        padding_length = data[-1]
        return data[:-padding_length]
    
    def countSetup(self):
        if(self.setupCounter != 4):
            return True
        else :
            return False

    def recieve(self):
        while self.running :
            try:
                message = self.socket.recv(2048)
                if(self.countSetup()):
                    messageDecode = message[0:20].decode('utf-8')
                else :
                    messageDecode = "MESSAGE"

                if(messageDecode == 'PUBLIC-1'):
                    self.socket.send(str(self.publicKey[0]).encode('utf-8'))
                    self.setupCounter +=1
                elif(messageDecode == 'PUBLIC-2'):
                    self.socket.send(str(self.publicKey[1]).encode('utf-8'))
                    self.setupCounter +=1
                elif(messageDecode == 'NICK'):
                    self.socket.send(self.nickname.encode('utf-8'))
                    self.setupCounter +=1
                elif(messageDecode.split("\n")[0] == 'ENCKEY'):
                    self.encryptKey = eval(message.decode('utf-8').split("\n")[1])
                    self.setupCounter +=1
                else :
                    message_parts = message.decode('utf-8').split("\n\nMESSAGE")
                    if(len(message_parts) > 1):
                        key = message_parts[1].split("\n\n")
                        public_1 = key[0]
                        public_2 = key[1]
                        encryptMessage = eval(message_parts[0])
                        decryptMessage = AES.new(self.encryptKey, AES.MODE_ECB).decrypt(encryptMessage)
                        messageWithSignature = self.unpad_data(decryptMessage).decode('utf-8')
                    if(len(messageWithSignature.split("\n\nSIGNATURE_BEGIN")) > 1):
                        valid = self.verify(messageWithSignature, public_1, public_2)
                        if(valid):
                            message = messageWithSignature.split("\n\nSIGNATURE_BEGIN")[0]
                        else :
                            sender = messageWithSignature.split("\n\nSIGNATURE_BEGIN")[0].split(" : ")[0]
                            message = f"{sender} : This Message Have Been Interrupted"
                    else :
                        message = eval(message_parts[0])
                        message = AES.new(self.encryptKey, AES.MODE_ECB).decrypt(message)
                        message = self.unpad_data(message).decode('utf-8')

                    if(self.gui_done):
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except :
                print('Error')
                self.socket.close()
                break

client = Client(HOST, PORT)