# Python program to implement client side of chat room.
import socket
import select
import sys
import struct
 
def pack_packet(version: int, operation: int, input: str) -> bytes:
    data = bytes(input, 'utf-8')
    data_len = struct.pack("!I", len(data))
    packet_len = struct.pack("!I", 4 + 1 + 4 + len(data))
    return packet_len + struct.pack("!IBI", version, operation, data_len) + data

def unpack_packet(packet: bytes) -> tuple:
    packet_len = struct.unpack("!I", packet[:4])[0]
    version, operation = struct.unpack("!BI", packet[4: 9])
    data_len = struct.unpack("!I", packet[9: 13])[0]
    data = packet[13: 13 + data_len]
    return version, data

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print ("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))
 
while True:
 
    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]
 
    """ There are two possible input situations. Either the
    user wants to give manual input to send to other people,
    or the server is sending a message to be printed on the
    screen. Select returns from sockets_list, the stream that
    is reader for input. So for example, if the server wants
    to send a message, then the if condition will hold true
    below.If the user wants to send a message, the else
    condition will evaluate as true"""
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
 
    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            version, operation, data = unpack_packet(message)
            print(version, operation, data)
        else:
            message = sys.stdin.readline()
            output = pack_packet(1, 1, message)
            server.send(output)
            sys.stdout.write("<You>")
            sys.stdout.write(message)
            sys.stdout.flush()
server.close()