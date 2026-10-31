
import threading
from libs.middleware import MiddleWare ,PING
import time
class Latency(threading.Thread):

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.running = True
        self.last_ping = 0.0


    def run(self):
        while self.running:
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


