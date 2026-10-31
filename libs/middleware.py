import struct
import zlib
TYPE_LOGIN = 1
TYPE_LOGIN_OK = 2
TYPE_GMSG = 3
COUNT_CONN = 0x56
HEADER_FMT = "!IBBBII"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
EXIT=0x64
PING=0X57
EXIT_MSG=0x65
PONG=0x58
MAGIC = 0x737269
VERSION = 1
SIG=0x68
SIG_FAIL=0x67
SHARE_GROUP_KEY=0x60
RECV_GROUP_KEY=0x63
AUTH_FAIL=0x66
U_JOIN=0x61
I_KEYS=0x62
SIG_PASS=0X68



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
        try:
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
        except OSError:
            print('Cleanup the Session')
            sock.close()

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