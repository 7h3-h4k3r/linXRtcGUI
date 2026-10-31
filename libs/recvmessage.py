from libs.middleware import MiddleWare , PONG , TYPE_GMSG , U_JOIN, RECV_GROUP_KEY ,I_KEYS,COUNT_CONN,SHARE_GROUP_KEY, EXIT ,EXIT_MSG , TYPE_LOGIN ,TYPE_LOGIN_OK
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import struct
from . import peer_group_key ,peer_public_key ,my_sender_key
from cryptography.hazmat.primitives.asymmetric import rsa, padding 
from cryptography.hazmat.primitives import serialization, hashes
import json
import threading
import time
from src.themeClass import Theme
from cryptography.hazmat.primitives import serialization
from libs.route import  routeR
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
        global my_sender_key
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
        version, sender_len, key_len = struct.unpack_from("!BBH", payload, 0)
        
        sender_start = 4
        sender_end = sender_start + sender_len
        sender_username = payload[sender_start:sender_end].decode("utf-8")
        
        key_start = sender_end
        key_end = key_start + key_len
        enc_key = payload[key_start:key_end]
        
        return sender_username, enc_key


    def receive_group_message(self, payload):
  
        if len(payload) < 31:
            raise ValueError("Invalid broadcast payload: too short")

        username_len = struct.unpack("!H", payload[:2])[0]
        offset = 2

        if offset + username_len + 28 > len(payload):
            raise ValueError("Incomplete broadcast payload: truncated username or ciphertext")

        username = payload[offset:offset + username_len].decode("utf-8")
        offset += username_len

        nonce = payload[offset:offset + 12]
        offset += 12

        ciphertext = payload[offset:]

        if username == self.username:
            aes = self.aesgcm
        elif username in peer_group_key:
            aes = AESGCM(peer_group_key[username])
        else:
            raise KeyError(f"Missing decryption key for user: {username}")

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
            user_name=self.username,
            encryption_mode='EndToEnd Encryption',
            auth_type='Signup & Login'
        )
        self.chatplace.status_bar.update_status(connection_state='online',connection_text='Connected')
        try:
            packet = 0
            while self.running:
                packet_type, payload = MiddleWare.recv_packet(self.sock)
                if packet_type is None:
                    break
                packet +=1
                if packet_type == TYPE_GMSG:
                    try:
                        msg = self.receive_group_message(payload)
                        if msg:
                            routeR.group_message_send(self.chatplace.chat_area, self.handler, msg)
                    except Exception as err:
                        print(f"Error handling TYPE_GMSG: {err}")
                    
                    self.chatplace.right_panel.update_client_log("We recv Message ", Theme.YELLOW)
                
                elif packet_type == U_JOIN:
                    print('new user joined bro lets see our who he are ')
                    username, pubkey = self.get_user_and_pubkey(payload)
                    print(username, pubkey)
                    rsa_pub = serialization.load_pem_public_key(pubkey.encode())
                    peer_public_key[username] = rsa_pub
                    self.send_key_to(username, rsa_pub)
                    self.chatplace.right_panel.update_client_log(username + ' Joined', Theme.GREEN)

                elif packet_type == RECV_GROUP_KEY:
                    sender_username, enc_key = self.unpack_shared_key(payload)
                    self.chatplace.right_panel.update_client_log(f"Received shared key from {sender_username}")
                    
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
                    self.chatplace.right_panel.update_client_log("Recv all pubkeys", Theme.BLUE)

                    for user, pem in data['keys'].items():
                        if user != self.username:
                            rsa_pub = serialization.load_pem_public_key(pem.encode())
                            peer_public_key[user] = rsa_pub
                            self.send_key_to(user, rsa_pub)
                    self.chatplace.right_panel.update_client_log("SenderKey shared", Theme.BLUE)
                
                elif packet_type == COUNT_CONN:
                    self.chatplace.right_panel.update_info(connected_users=payload[0])
                    print("Connection Details", payload)

                elif packet_type == PONG:
                    latency_is = (time.monotonic() - self.latency.last_ping) * 1000
                    print(f"Latency: {latency_is:.2f} ms")
                    self.chatplace.right_panel.update_info(latency=f"{latency_is:.2f} ms")
                    self.chatplace.status_bar.update_status(ping=latency_is)

                    routeR.set_latency(latency_is, self.chatplace.right_panel)

                elif packet_type == EXIT:
                    print("Received EXIT packet from server")
                    break
                elif packet_type == EXIT_MSG:
                    username = payload.decode('utf-8', errors='ignore').strip('\x00')
                    msg = f"{username} Disconnected"
                    self.chatplace.right_panel.update_client_log(msg, Theme.RED)
            
                else:
                    packet-=1
                    print("Packet:", packet_type)
                self.chatplace.status_bar.update_status(packet_count=packet)

        except Exception as e:
            print(f"Disconnected due to error: {e}")
        finally:
            print("Cleaning up session...")
            self.running = False
            
            if getattr(self, "latency", None):
                try:
                    self.latency.stop()
                except Exception:
                    pass

            if getattr(self, "sock", None):
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None

            # Clear cryptographic keys/session state
            peer_public_key.clear()
            peer_group_key.clear()
            

    def stop(self):
        self.running = False
        self.thread.join()
