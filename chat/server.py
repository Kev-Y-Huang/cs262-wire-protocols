import logging
import socket
import sys
from _thread import *
from concurrent import futures

import grpc
import grpc_proto.chat_pb2_grpc as chat_pb2_grpc
from grpc_proto.server import ChatServer
from utils import get_server_config_from_file
from wire.server import client_thread
from wire.chat_service import Chat

# global variables and configurations
YAML_CONFIG_PATH = '../config.yaml'
IP_ADDRESS, PORT = get_server_config_from_file(YAML_CONFIG_PATH)
logging.basicConfig(format='[%(asctime)-15s]: %(message)s', level=logging.INFO)


def main():
    # Check if enough arguments are passed
    if len(sys.argv) != 2:
        print('Correct usage: python client.py [implementation]')
        exit()

    # Wire protocol implementation of the client
    if sys.argv[1] == 'wire':
        # Setting up the server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((IP_ADDRESS, PORT))
        server.listen(5)

        logging.info('Starting Wire Protocol Server')

        chat_app = Chat()

        while True:
            try:
                """Accepts a connection request and stores two parameters,
                conn which is a socket object for that user, and addr
                which contains the IP address of the client that just
                connected"""
                conn, addr = server.accept()

                # prints the address of the user that just connected
                print(addr[0] + " connected")

                # creates and individual thread for every user
                # that connects
                start_new_thread(client_thread, (chat_app, conn, addr))
            except KeyboardInterrupt:
                logging.info('Stopping Server')
                break

        conn.close()
        server.close()
    # grpc implementation of the client
    elif sys.argv[1] == 'grpc':
        # Start a ChatServer Servicer
        service = ChatServer()

        # Setup the grpc server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_pb2_grpc.add_ChatServerServicer_to_server(service, server)

        logging.info('Starting GRPC Server')
        server.add_insecure_port(f'{IP_ADDRESS}:{PORT}')
        server.start()

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            logging.info('Stopping Server')
            service.is_connected = False
    else:
        print('')

if __name__ == "__main__":
    main()