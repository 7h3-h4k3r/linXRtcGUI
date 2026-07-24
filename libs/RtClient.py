import struct
import zlib
import socket
import struct
import threading


TYPE_LOGIN = 1
TYPE_LOGIN_OK = 2
TYPE_GMSG = 3
COUNT_CONN = 0x56
HEADER_FMT = "!IBBBII"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
SET_LATANCY=0X59
PING=0X57
PONG=0x58
MAGIC = 0x737269
VERSION = 1


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


class recvMessage(threading.Thread):
    def __init__(self,sock,handler,chatplace):
        super().__init__()
        self.sock = sock 
        self.handler = handler
        self.chatplace = chatplace
    
    def run(self):
        print("Recving Message from the LinXRTC server recvMessage() Threading start\n")
        while True:
            try:
                packet_type, payload = MiddleWare.recv_packet(self.sock)

                if packet_type == TYPE_GMSG:
                    length = payload[0]
                    msg = payload[1:1 + length].decode()
                    routeR.group_message_send(self.chatplace.chat_area,self.handler,msg)
                elif packet_type == COUNT_CONN:
                    self.chatplace.right_panel.update_info(
                            connected_users=payload[0],
                        )
                    print("Connection Deails",payload)
                elif packet_type == PING:
                    print('i am send PONG admin')
                    MiddleWare.send_packet(self.sock,PONG, b"")
                elif packet_type == SET_LATANCY:
                    
                    print('i am getting latancyy' ,payload[0])
                else:
                    print("Packet:", packet_type)

            except Exception as e:
                print("Disconnected:", e)
                break   
    
class RtClient:
    
    def __init__(self,ip,port):
        self.ip = ip 
        self.port = port 
        self.sock = None
   
              
    def on_send_message_sock(self,msg):
        try:
            
            payload = (
                struct.pack("!B", len(msg.encode())) +
                msg.encode()
            )

            MiddleWare.send_packet(self.sock, TYPE_GMSG, payload)
                    
            print("packe sending...")
            
                
        except (BrokenPipeError, ConnectionResetError):
            print("Disconnected")
            self.sock.close()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.sock.close()

    def setRecv(self,handler,chat_frame):
        recv_threading = recvMessage(self.sock,handler,chat_frame)
        recv_threading.start()

    def start(self,username,password):
        self.sock = socket.socket()
        self.sock.connect((self.ip, self.port))

        username = username.encode()
        password = password.encode()

        payload = (
            struct.pack("!B", len(username)) +
            username +
            struct.pack("!B", len(password)) +
            password
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

        
    