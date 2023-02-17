import struct

# Packet format:
# - 4 byte unsigned integer for packet length (M)
# - 4 byte unsigned integer for version number
# - 4 byte unsigned integer for data length (N)
# - 1 byte unsigned integer for operation code
# - N bytes for packet data

def pack_packet(operation: int, input: str) -> bytes:
    data = input.encode('utf-8')
    packet_len = struct.pack("!I", 4 + 4 + 1 + len(data))
    return packet_len + struct.pack("!IB", len(data), operation) + data

def unpack_packet(packet: bytes) -> tuple:
    data_len, operation = struct.unpack("!IB", packet[:5])
    data = packet[5:5 + data_len]
    output = data.decode('utf-8')
    return operation, output

# Example usage:
operation = 10
data = "Hello, World!"
packet = pack_packet(operation, data)
unpacked_operation, unpacked_data = unpack_packet(packet)

assert operation == unpacked_operation
assert data == unpacked_data