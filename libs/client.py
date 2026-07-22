import struct
import zlib
import socket
import struct
import threading

TYPE_LOGIN = 1
TYPE_LOGIN_OK = 2
TYPE_GMSG = 3
HEADER_FMT = "!IBBBII"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

MAGIC = 0x737269
VERSION = 1




def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            raise ConnectionError("Connection closed")

        data += chunk

    return data


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


def recv_packet(sock):
    header = recv_exact(sock, HEADER_SIZE)

    magic, version, packet_type, flags, length, checksum = struct.unpack(
        HEADER_FMT,
        header
    )

    if magic != MAGIC:
        raise ValueError("Invalid magic number")

    payload = recv_exact(sock, length)

    if zlib.crc32(payload) != checksum:
        raise ValueError("Checksum failed")

    return packet_type, payload


def recv_loop(sock):
    while True:
        try:
            packet_type, payload = recv_packet(sock)

            if packet_type == TYPE_GMSG:
                length = payload[0]
                msg = payload[1:1 + length].decode()
                print(msg)

            else:
                print("Packet:", packet_type)

        except Exception as e:
            print("Disconnected:", e)
            break
def start(username,password):
    sock = socket.socket()
    sock.connect(("127.0.0.1", 7878))

    username = username.encode()
    password = password.encode()

    payload = (
        struct.pack("!B", len(username)) +
        username +
        struct.pack("!B", len(password)) +
        password
    )

    send_packet(sock, TYPE_LOGIN, payload)

    packet_type, payload = recv_packet(sock)

    print(payload.decode())

    if packet_type == TYPE_LOGIN_OK:

        threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()

        while True:

            try:
                msg = input("> ")

                payload = (
                    struct.pack("!B", len(msg.encode())) +
                    msg.encode()
                )

                send_packet(sock, TYPE_GMSG, payload)
                
                print("packe sending...")
        
            
            except (BrokenPipeError, ConnectionResetError):
                print("Disconnected")
                break
            except Exception as e:
                import traceback
                traceback.print_exc()
                break

    sock.close()