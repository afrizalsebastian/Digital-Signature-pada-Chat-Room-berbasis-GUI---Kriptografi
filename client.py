import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from ECDSA import ECDSA

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
        self.text_area.config(state='disabled', font=('Space Mono', 16),height=20)

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

    def write(self):
        message = f"{self.nickname} : {self.input_message.get('1.0', 'end')}"
        message = self.sign(message, self.privateKey)
        self.socket.send(message.encode('utf-8'))
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

    def recieve(self):
        while self.running :
            try:
                message = self.socket.recv(2048).decode('utf-8')
                if(message == 'PUBLIC-1'):
                    self.socket.send(str(self.publicKey[0]).encode('utf-8'))
                elif(message == 'PUBLIC-2'):
                    self.socket.send(str(self.publicKey[1]).encode('utf-8'))
                elif(message == 'NICK'):
                    self.socket.send(self.nickname.encode('utf-8'))
                else :
                    message_parts = message.split("\n\nMESSAGE")
                    if(len(message_parts) > 1):
                        key = message_parts[1].split("\n\n")
                        public_1 = key[0]
                        public_2 = key[1]
                    messageWithSignature = message_parts[0]
                    if(len(messageWithSignature.split("\n\nSIGNATURE_BEGIN")) > 1):
                        valid = self.verify(messageWithSignature, public_1, public_2)
                        if(valid):
                            message = messageWithSignature.split("\n\nSIGNATURE_BEGIN")[0]
                        else :
                            sender = messageWithSignature.split("\n\nSIGNATURE_BEGIN")[0].split(" : ")[0]
                            message = f"{sender} : This Message Have Been Interrupted"
                    else :
                        message = message_parts[0]

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