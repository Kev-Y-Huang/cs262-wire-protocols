# Python program to implement server side of chat room.
import socket
import time

from _thread import *

from wire.chat_service import Chat, User
from wire.wire_protocol import pack_packet, unpack_packet

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP_ADDRESS = socket.gethostname()
PORT = 6666

"""
binds the server to an entered IP address and at the
specified port number.
The client must be aware of these parameters
"""
server.bind((IP_ADDRESS, PORT))

"""
listens for 1 active connection. This number can be
increased as per convenience.
"""
server.listen(5)

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
        break

conn.close()
server.close()
