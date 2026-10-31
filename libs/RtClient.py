import struct

import socket
import struct
import threading
import time
import json
from os import urandom
from src.themeClass import Theme
from . import peer_group_key ,peer_public_key , my_sender_key
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from libs.middleware import MiddleWare
from libs.route import routeR
from libs.recvmessage import recvMessage
from libs.latency import Latency
from libs.middleware import SIG , SIG_FAIL,SIG_PASS , EXIT ,TYPE_GMSG ,TYPE_LOGIN,TYPE_LOGIN_OK,AUTH_FAIL

class RtClient:
    
    def __init__(self,ip,port):
        self.ip = ip 
        self.port = port 
        self.sock = None
        self.my_priv_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.my_pub_pem = self.my_priv_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        print('MY Pub Key ',self.my_pub_pem)
        self.sock = socket.socket()
        self.sock.connect((self.ip, self.port))
        global my_sender_key 
        my_sender_key = AESGCM.generate_key(bit_length=256)
       
        self.aesgcm = AESGCM(my_sender_key)
    
            

            
        
    def signup(self, username, password, email):
    
        user_info = {
            "username": username,
            "password": password,
            "email": email
        }

        try:

            payload = json.dumps(user_info).encode("utf-8")

            MiddleWare.send_packet(self.sock, SIG, payload)
            packet_type, resp_payload = MiddleWare.recv_packet(self.sock)

            if resp_payload:
                print(resp_payload.decode("utf-8", errors="replace"))
            print(packet_type)
            if packet_type == SIG_PASS:
                return True
            elif packet_type == SIG_FAIL:
                return False
            else:
                print(f"Unexpected packet type received: {packet_type}")
                return False

        except (BrokenPipeError, ConnectionResetError):
            print("Disconnected from server.")
            self.sock.close()
            return False
        except Exception as e:
            traceback.print_exc()
            self.sock.close()
            return False
        
    def exit(self):
        MiddleWare.send_packet(self.sock,EXIT, b'')


    def on_send_message_sock(self,msg):

       
        nonce = urandom(12)

        ciphertext = self.aesgcm.encrypt(nonce,msg.encode(),None)
        try:
            
            payload = nonce + ciphertext

            MiddleWare.send_packet(self.sock, TYPE_GMSG, payload)
                    
            print("packe sending...")
            
                
        except (BrokenPipeError, ConneacketconfigctionResetError):
            print("Disconnected")
            self.sock.close()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.sock.close()

    def setRecv(self,handler,chat_frame,username):
        latency = Latency(self.sock)
        recv_threading = recvMessage(self.sock,handler,chat_frame,latency,self.aesgcm,self.my_priv_key,username)
        latency.start()
        recv_threading.start()
    
    def start(self,username,password):
        
        print(self.my_pub_pem)

        username = username.encode()
        password = password.encode()
        public_key = self.my_pub_pem.encode()

        payload = (
            struct.pack("!B", len(username)) +
            username +
            struct.pack("!B", len(password)) +
            password +
            struct.pack("!H" ,len(public_key)) +
            public_key
        )

        MiddleWare.send_packet(self.sock, TYPE_LOGIN, payload)

        packet_type, payload = MiddleWare.recv_packet(self.sock)

        print(payload.decode())
        try:
            if packet_type == TYPE_LOGIN_OK:
                return True
            elif packet_type == AUTH_FAIL:
                print('i recived auth failed')
                return False
                
        except (BrokenPipeError, ConnectionResetError):
            print("Disconnected")
            self.sock.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.sock.close()

        
    