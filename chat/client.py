# Python program to implement client side of chat room.
import socket
import select
import sys

import re

from wire_protocol import pack_packet, unpack_packet

ERROR_MSG = """Invalid input string, please use format <command>|<text>\n
0| -> list user accounts\n
1|<username> -> create an account with name username\n
2|<username> -> delete an account with name username\n
3|<username>|<text> -> send message to username\n
4| -> deliver all unsent messages to current user\n"""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_ADDRESS = 12345
PORT = 12345
server.connect((IP_ADDRESS, PORT))

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    """There are two possible input situations. Either the
    user wants to give manual input to send to other people,
    or the server is sending a message to be printed on the
    screen. Select returns from sockets_list, the stream that
    is reader for input. So for example, if the server wants
    to send a message, then the if condition will hold true
    below. If the user wants to send a message, the else
    condition will evaluate as true"""
    read_sockets, write_socket, error_socket = select.select(
        sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            version, operation, data = unpack_packet(message)
            print(version, operation, data)
        else:
            usr_input = sys.stdin.readline()

            # Parses the user input to see if it is a valid input
            match = re.match(r"(\d)\|((\S| )+)", usr_input)
            if match:
                op_code, message = match

                # Encodes the message
                output = pack_packet(op_code, message)
                server.send(output)

                if op_code == 5:
                    break
            else:
                sys.stdout.write()
                sys.stdout.write(ERROR_MSG)
                sys.stdout.flush()
server.close()
