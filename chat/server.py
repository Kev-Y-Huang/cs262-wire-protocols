# Python program to implement server side of chat room.
import socket
import select
import sys

from _thread import *
import threading

from utils import Chat
from wire_protocol import pack_packet, unpack_packet

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP_ADDRESS = 12345
PORT = 12345
server.connect((IP_ADDRESS, PORT))

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
server.listen(1)

chat_app = Chat()

accounts = {}
online_users = set()


def clientthread(conn, addr):

    # sends a message to the client whose user object is conn
    message = 'Connected to server'
    output = pack_packet(1, 1, message)
    conn.send(output)

    while True:
        try:
            data = conn.recv(2048)
            op_code, message = unpack_packet(data)

            if message:
                chat_app.handler(op_code, message)

                """prints the message and address of the
                user who just sent the message on the server
                terminal"""
                print("<" + addr[0] + "> " + op_code + "|" + message)

            else:
                """message may have no content if the connection
                is broken, in this case we remove the connection"""
                remove(conn)

        except:
            continue


"""Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """


def broadcast(message, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(message)
            except:
                clients.close()

                # if the link is broken, we remove the client
                remove(clients)


"""The following function simply removes the object
from the list that was created at the beginning of
the program"""


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)


def main():
    while True:

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

    conn.close()
    server.close()
