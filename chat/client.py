# Python program to implement client side of chat room.
import socket
import select
import sys
import platform
import re
import threading
from threading import *

from wire_protocol import pack_packet, unpack_packet

ERROR_MSG = """Invalid input string, please use format <command>|<text>
    0|                  -> list user accounts
    1|<username>        -> create an account with name username
    2|<username>        -> login to an account with name username
    3|                  -> logout from current account
    4|                  -> delete current account
    5|<username>|<text> -> send message to username
    6|                  -> deliver all unsent messages to current user"""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setup connection to server socket
IP_ADDRESS = socket.gethostname()
PORT = 6666
server.connect((IP_ADDRESS, PORT))

class receive_messages(Thread):
    def run(self):
        while True:
            try:
                message = server.recv(1024)
                operation, data = unpack_packet(message)
                print(data)
            except KeyboardInterrupt:
                break

t1 = receive_messages()
t1.start()
while True:
    try:
        usr_input = input()
        if usr_input == "quit":
            sys.exit()
        else:
            if usr_input != '':
                # Parses the user input to see if it is a valid input
                match = re.match(r"(\d)\|((\S| )*)", usr_input)
                if match:
                    op_code, message = int(match.group(1)), match.group(2)
                    output = pack_packet(op_code, message)
                    server.send(output)
                else:
                    print(ERROR_MSG)
    except KeyboardInterrupt:
        break
server.close()
