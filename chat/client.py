# Python program to implement client side of chat room.
import socket
import select
import sys
import platform

if platform.system() == 'Windows':
    import msvcrt

import re

from wire_protocol import pack_packet, unpack_packet

ERROR_MSG = """Invalid input string, please use format <command>|<text>
    0|                  -> list user accounts
    1|<username>        -> create an account with name username
    2|<username>        -> login to an account with name username
    3|<username>        -> logout from current account
    4|                  -> delete current account
    5|<username>|<text> -> send message to username
    6|                  -> deliver all unsent messages to current user"""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setup connection to server socket
IP_ADDRESS = socket.gethostname()
PORT = 6666
server.connect((IP_ADDRESS, PORT))

while True:
    try:
        # maintains a list of possible input streams
        sockets_list = [server]

        """There are two possible input situations. Either the
        user wants to give manual input to send to other people,
        or the server is sending a message to be printed on the
        screen. Select returns from sockets_list, the stream that
        is reader for input. So for example, if the server wants
        to send a message, then the if condition will hold true
        below. If the user wants to send a message, the else
        condition will evaluate as true"""
        read_sockets, write_socket, error_socket = select.select(
            sockets_list, [], [], 0.1)
        
        # select.select on Windows only supports sockets so have
        # to use msvcrt to add polling for standard input as per
        # https://stackoverflow.com/a/46823814
        if platform.system() == 'Windows':
            if msvcrt.kbhit():
                read_sockets.append(sys.stdin)
        else:
            read_sockets.append(sys.stdin)

        for socks in read_sockets:
            if socks == server:
                message = socks.recv(2048)
                operation, data = unpack_packet(message)
                print(data)
            else:
                usr_input = sys.stdin.readline()

                # Parses the user input to see if it is a valid input
                match = re.match(r"(\d)\|((\S| )*)", usr_input)
                if match:
                    op_code, message = int(match.group(1)), match.group(2)

                    # Encodes the message
                    output = pack_packet(op_code, message)
                    server.send(output)

                    if op_code == 5:
                        break
                else:
                    print(ERROR_MSG)
    except KeyboardInterrupt:
        break
server.close()
