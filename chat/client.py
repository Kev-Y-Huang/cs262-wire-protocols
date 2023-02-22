import re
import socket
import sys
from threading import *

from grpc_proto.client import ChatClient
from utils import get_server_config_from_file
from wire.client import ReceiveMessages
from wire.wire_protocol import pack_packet

# global variables
YAML_CONFIG_PATH = '../config.yaml'
ERROR_MSG = """Invalid input string, please use format <command>|<text>
    0|                  -> list user accounts
    1|<username>        -> create an account with name username
    2|<username>        -> login to an account with name username
    3|                  -> logout from current account
    4|                  -> delete current account
    5|<username>|<text> -> send message to username
    6|                  -> deliver all unsent messages to current user"""


def main():
    # Check if enough arguments are passed
    if len(sys.argv) != 2:
        print('Correct usage: python client.py [implementation]')
        exit()

    ip_address, port = get_server_config_from_file(YAML_CONFIG_PATH)

    # Wire protocol implementation of the client
    if sys.argv[1] == 'wire':
        # Setup connection to server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((ip_address, port))

        t1 = ReceiveMessages(server)
        t1.start()
        while True:
            try:
                usr_input = input('<you> ')
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
    # grpc implementation of the client
    elif sys.argv[1] == 'grpc':
        chat = ChatClient(ip_address, port)

        while True:
            usr_input = input('<you> ')
            if usr_input == "quit":
                sys.exit()
            else:
                if usr_input != '':
                    # Parses the user input to see if it is a valid input
                    match = re.match(r"(\d)\|((\S| )*)", usr_input)
                    if match:
                        op_code, message = int(match.group(1)), match.group(2)
                        chat.handler(op_code, message)
                    else:
                        print(ERROR_MSG)


if __name__ == "__main__":
    main()