import logging
import socket
import sys
import time
from _thread import *
from concurrent import futures

import grpc
import grpc_proto.chat_pb2_grpc as chat_pb2_grpc
from grpc_proto.server import ChatServer
from utils import get_server_config_from_file
from wire.chat_service import Chat, User
from wire.wire_protocol import pack_packet, unpack_packet

YAML_CONFIG_PATH = '../config.yaml'


def main():
    if len(sys.argv) != 2:
        print('Correct usage: python client.py [implementation]')
        exit()

    ip_address, port = get_server_config_from_file(YAML_CONFIG_PATH)
    logging.basicConfig(format='[%(asctime)-15s]: %(message)s', level=logging.INFO)

    if sys.argv[1] == 'wire':
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((ip_address, port))
        server.listen(5)

        logging.info('Starting Wire Protocol Server')

        chat_app = Chat()

        def clientthread(conn, addr):

            # sends a message to the client whose user object is conn
            message = '<server> Connected to server'
            output = pack_packet(1, message)
            conn.send(output)

            curr_user = User(conn)

            while True:
                try:
                    data = conn.recv(2048)

                    if data:
                        op_code, contents = unpack_packet(data)

                        """prints the message and address of the
                        user who just sent the message on the server
                        terminal"""
                        print(f"<{addr[0]}> {op_code}|{contents}")

                        responses = chat_app.handler(
                            int(op_code), curr_user, contents)

                        for recip_conn, response in responses:
                            output = pack_packet(1, response)
                            recip_conn.send(output)
                            time.sleep(0.1)

                    # If data has no content, we remove the connection
                    else:
                        chat_app.handler(3, curr_user)

                except:
                    break


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
                start_new_thread(clientthread, (conn, addr))
            except KeyboardInterrupt:
                logging.info('Stopping Server')
                break

        conn.close()
        server.close()
    elif sys.argv[1] == 'grpc':
        service = ChatServer()

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_pb2_grpc.add_ChatServerServicer_to_server(service, server)

        logging.info('Starting GRPC Server')
        server.add_insecure_port(f'{ip_address}:{port}')
        server.start()

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            logging.info('Stopping Server')
            service.is_connected = False

if __name__ == "__main__":
    main()