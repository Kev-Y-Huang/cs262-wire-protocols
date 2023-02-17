import struct

# Packet format:
# - 4 byte unsigned integer for packet length (M)
# - 4 byte unsigned integer for version number
# - 4 byte unsigned integer for data length (N)
# - 1 byte unsigned integer for operation code
# - N bytes for packet data

def pack_packet(version: int, operation: int, input: str) -> bytes:
    data = input.encode('utf-8')
    packet_len = struct.pack("!I", 4 + 4 + 1 + len(data))
    return packet_len + struct.pack("!IIB", version, len(data), operation) + data

def unpack_packet(packet: bytes) -> tuple:
    packet_len = struct.unpack("!I", packet[:4])[0]
    version, data_len, operation = struct.unpack("!IIB", packet[4: 13])
    data = packet[13: 13 + data_len]
    output = data.decode('utf-8')
    return version, operation, output

# Example usage:
version = 1
operation = 10
data = "Hello, World!"
packet = pack_packet(version, operation, data)
unpacked_version, unpacked_operation, unpacked_data = unpack_packet(packet)

assert version == unpacked_version
assert operation == unpacked_operation
assert data == unpacked_data