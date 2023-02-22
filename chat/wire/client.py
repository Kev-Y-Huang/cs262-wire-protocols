
from threading import *

from wire.wire_protocol import unpack_packet
from utils import print_with_prompt


class ReceiveMessages(Thread):
    def __init__(self, server):
        super().__init__()
        self.__server = server

    def run(self):
        while True:
            try:
                message = self.__server.recv(1024)
                _, data = unpack_packet(message)
                print_with_prompt(data)
            except:
                break
