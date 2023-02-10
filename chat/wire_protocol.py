import struct

# # Packet format:
# # - 4 byte unsigned integer for version number
# # - 1 byte unsigned integer for operation code
# # - 4 byte unsigned integer for data length (N)
# # - N bytes for packet data
# # - 4 byte unsigned integer for packet length (M)

# def pack_packet(version: int, operation: int, input: str) -> bytes:
#     data = input.encode('utf-8')
#     data_len = len(data)
#     packet_len = struct.pack("!I", 4 + 1 + 4 + data_len)
#     return packet_len + struct.pack("!IBI", version, operation, data_len) + data

# def unpack_packet(packet: bytes) -> tuple:
#     packet_len = struct.unpack("!I", packet[:4])[0]
#     version, operation = struct.unpack("!BI", packet[4: 9])
#     data_len = struct.unpack("!I", packet[9: 13])[0]
#     data = packet[13: 13 + data_len]
#     return version, operation, data

# # Example usage:
# version = 1
# operation = 1
# data = "Hello, World!"
# packet = pack_packet(version, operation, data)
# unpacked_version, unpacked_operation, unpacked_data = unpack_packet(packet)

# print(unpacked_version)
# print(unpacked_operation)

# assert version == unpacked_version
# assert operation == unpacked_operation
# assert data == unpacked_data

# Packet format:
# - 4 byte unsigned integer for packet length (M)
# - 4 byte unsigned integer for version number
# - 4 byte unsigned integer for data length (N)
# - 1 byte unsigned integer for operation code
# - N bytes for packet data

def pack_packet(version: int, operation: int, data: bytes) -> bytes:
    data_len = struct.pack("!I", len(data))
    packet_len = struct.pack("!I", 4 + 4 + 1 + len(data))
    return packet_len + struct.pack("!IIB", version, len(data), operation) + data

def unpack_packet(packet: bytes) -> tuple:
    packet_len = struct.unpack("!I", packet[:4])[0]
    version, data_len, operation = struct.unpack("!IIB", packet[4: 13])
    data = packet[13: 13 + data_len]
    return version, operation, data

# Example usage:
version = 1
operation = 10
data = b"Hello, World!"
packet = pack_packet(version, operation, data)
unpacked_version, unpacked_operation, unpacked_data = unpack_packet(packet)

assert version == unpacked_version
assert operation == unpacked_operation
assert data == unpacked_data