import struct
import zlib
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
TYPE_LOGIN = 1
TYPE_LOGIN_OK = 2
TYPE_GMSG = 3
COUNT_CONN = 0x56
HEADER_FMT = "!IBBBII"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

PING=0X57
PONG=0x58
MAGIC = 0x737269
VERSION = 1
SHARE_GROUP_KEY=0x60
RECV_GROUP_KEY=0x63

U_JOIN=0x61
I_KEYS=0x62



class MiddleWare:
    @staticmethod
    def recv_exact(sock, size):
        data = b""

        while len(data) < size:
            chunk = sock.recv(size - len(data))

            if not chunk:
                raise ConnectionError("Connection closed")

            data += chunk

        return data

    @staticmethod
    def send_packet(sock, packet_type, payload, flags=0):
        checksum = zlib.crc32(payload)

        header = struct.pack(
            HEADER_FMT,
            MAGIC,
            VERSION,
            packet_type,
            flags,
            len(payload),
            checksum
        )

        sock.sendall(header+payload)

    @staticmethod
    def recv_packet(sock):
        header = MiddleWare.recv_exact(sock, HEADER_SIZE)

        magic, version, packet_type, flags, length, checksum = struct.unpack(
            HEADER_FMT,
            header
        )

        if magic != MAGIC:
            raise ValueError("Invalid magic number")

        payload = MiddleWare.recv_exact(sock, length)

        if zlib.crc32(payload) != checksum:
            raise ValueError("Checksum failed")

        return packet_type, payload

class routeR:

    @staticmethod
    def group_message_send(chatplace,handler,msg):
        result = msg.split(":")
        new_message = ' '.join(result[1:])
        other_message=f"{result[0].strip()}\n{new_message.strip()}"
        chatplace.add_message(handler,other_message)

    @staticmethod
    def set_latency(latency ,right_panel):

        value= None
        
        if latency <= 50:
            value=("Excellent", Theme.GREEN)
        elif latency <= 100:
            value=("Good", Theme.ORANGE)
        elif latency <= 200:
            value=("Fair", Theme.YELLOW)
        elif latency <= 300:
            value=("Poor", Theme.BLUE)
        else:
            value=("Very Poor",Theme.RED)

        right_panel.update_info(
            connection_quality=(value[0], value[1])
        )


class Latency(threading.Thread):

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.running = True
        self.last_ping = 0.0


    def run(self):
        while self.running:
            print('i am sending the ping')
            self.last_ping = time.monotonic()

            MiddleWare.send_packet(
                self.sock,
                PING,
                b""
            )

            time.sleep(10)
    def stop(self):
        self.running = False
        self.thread.join()



class recvMessage(threading.Thread):
    def __init__(self,sock,handler,chatplace,latency,aesgcm,pri_key,username):
        super().__init__()
        self.sock = sock 
        self.running = True
        self.handler = handler
        self.chatplace = chatplace
        self.latency = latency
        self.aesgcm = aesgcm
        self.pri_key = pri_key
        self.username = username
    

    def send_key_to(self,target_user,rsa_pub):
        enc_key = rsa_pub.encrypt(
            my_sender_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        print('I AM SENDING MY SHARE KEY',my_sender_key)
        payload = (
            
            struct.pack("!B", len(target_user.encode()))+
            target_user.encode() + 
            struct.pack("!H", len(enc_key)) +
            enc_key 
            
        )

        MiddleWare.send_packet(self.sock,SHARE_GROUP_KEY,payload)

    
    def unpack_shared_key(self,payload: bytes):
        # Header: version (1), sender_len (1), key_len (2) -> 4 bytes
        version, sender_len, key_len = struct.unpack_from("!BBH", payload, 0)
        
        sender_start = 4
        sender_end = sender_start + sender_len
        sender_username = payload[sender_start:sender_end].decode("utf-8")
        
        key_start = sender_end
        key_end = key_start + key_len
        enc_key = payload[key_start:key_end]
        
        return sender_username, enc_key


    def receive_group_message(self, payload):
        # Minimum size: 2 (username_len) + at least 1 (username) + 12 (nonce) + 16 (AES-GCM tag) = 31 bytes
        if len(payload) < 31:
            raise ValueError("Invalid broadcast payload: too short")

        # 1. Read username length
        username_len = struct.unpack("!H", payload[:2])[0]
        offset = 2

        # 12 bytes nonce + 16 bytes min tag = 28 bytes minimum crypto overhead
        if offset + username_len + 28 > len(payload):
            raise ValueError("Incomplete broadcast payload: truncated username or ciphertext")

        # 2. Read username
        username = payload[offset:offset + username_len].decode("utf-8")
        offset += username_len

        # 3. Read nonce (12 bytes)
        nonce = payload[offset:offset + 12]
        offset += 12

        # 4. Read ciphertext + tag
        ciphertext = payload[offset:]

        # 5. Look up the sender's shared key
        # (If using peer-to-peer shared keys, fallback to self.aesgcm if sender is self)
        if username == self.username:
            aes = self.aesgcm
        elif username in peer_group_key:
            aes = AESGCM(peer_group_key[username])
        else:
            raise KeyError(f"Missing decryption key for user: {username}")

        # 6. Decrypt and authenticate
        try:
            plaintext = aes.decrypt(nonce, ciphertext, None)
            message = plaintext.decode("utf-8")
            print(f"{username}: {message}")
            return f"{username} : {message}"
        except InvalidTag:
            raise ValueError(f"Authentication failed: invalid tag from {username}")

    def get_user_and_pubkey(self,payload):
        name_len = int.from_bytes(payload[:2],byteorder="big")
        offset = 2 

        username = payload[offset : offset + name_len].decode()

        public_key = payload[offset + name_len:].decode()

        return username,public_key
    
    def run(self):
        print("Recving Message from the LinXRTC server recvMessage() Threading start\n")
        self.chatplace.right_panel.update_info(
            encryption_mode='EndToEnd Encryption',
            auth_type='SIGNUP AND LOGIN'
        )
        while self.running:
            try:
                packet_type, payload = MiddleWare.recv_packet(self.sock)

                if packet_type == TYPE_GMSG:

                    try:
                        msg = self.receive_group_message(payload)
                        if msg:
                            routeR.group_message_send(self.chatplace.chat_area, self.handler, msg)
                    except Exception as err:
                        print(f"Error handling TYPE_GMSG: {err}")
                    
                    self.chatplace.right_panel.update_client_log(f"We recv Message ",Theme.YELLOW)
                  
                elif packet_type == U_JOIN:
                    print('new user joined bro lets see our who he are ')
                    username , pubkey = self.get_user_and_pubkey(payload)
                    print(username,pubkey)
                    rsa_pub = serialization.load_pem_public_key(pubkey.encode())
                    peer_public_key[username] = rsa_pub
                    self.send_key_to(username,rsa_pub)
                    self.chatplace.right_panel.update_client_log(username+' Joined',Theme.GREEN)
                elif packet_type == RECV_GROUP_KEY:
                    sender_username, enc_key = self.unpack_shared_key(payload)
                    self.chatplace.right_panel.update_client_log(f"Received shared key from {sender_username}")
                    
                    # Decrypt with your private RSA key
                    decrypted_key = self.pri_key.decrypt(
                        enc_key,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    peer_group_key[sender_username] = decrypted_key
                elif packet_type == I_KEYS:
                    data = json.loads(payload.decode("utf-8"))
                    received_keys = data["keys"]
                    self.chatplace.right_panel.update_client_log(f"Recv all pubkeys",Theme.BLUE)
                  

                    for user , pem in data['keys'].items():
                        if user != self.username:
                            rsa_pub = serialization.load_pem_public_key(pem.encode())
                            peer_public_key[user] = rsa_pub
                            self.send_key_to(user,rsa_pub)
                    self.chatplace.right_panel.update_client_log(f"SenderKey shared",Theme.BLUE)
                  
                elif packet_type == COUNT_CONN:
                    self.chatplace.right_panel.update_info(
                            connected_users=payload[0],
                        )
                    print("Connection Deails",payload)
                elif packet_type == PONG:
                    latency_is = (time.monotonic() - self.latency.last_ping) * 1000

                    print(f"Latacny :{latency_is:.2f} ms")

                    self.chatplace.right_panel.update_info(
                        latency=f"{latency_is:.2f} ms"
                    )
                    routeR.set_latency(latency_is,self.chatplace.right_panel)
               
                else:
                    print("Packet:", packet_type)

            except Exception as e:
                print("Disconnected:", e)
                break 
        

    def stop(self):
        self.running = False
        self.thread.join()
  
    
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
        
        global my_sender_key 
        my_sender_key = AESGCM.generate_key(bit_length=256)
       
        self.aesgcm = AESGCM(my_sender_key)

    

    

    def on_send_message_sock(self,msg):

       
        nonce = urandom(12)

        ciphertext = self.aesgcm.encrypt(nonce,msg.encode(),None)
        try:
            
            payload = nonce + ciphertext

            MiddleWare.send_packet(self.sock, TYPE_GMSG, payload)
                    
            print("packe sending...")
            
                
        except (BrokenPipeError, ConnectionResetError):
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
        self.sock = socket.socket()
        self.sock.connect((self.ip, self.port))
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
                
        except (BrokenPipeError, ConnectionResetError):
            print("Disconnected")
            self.sock.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.sock.close()

        
    