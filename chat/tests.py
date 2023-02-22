########################################
# Testing the wire protocol
########################################
print("****************************************")
print("***** Testing the wire protocol... *****")
print("****************************************")
from wire.wire_protocol import pack_packet, unpack_packet
import time

operation = 1
data = "Hello, World!"
packet = pack_packet(operation, data)
unpacked_operation, unpacked_data = unpack_packet(packet)

assert operation == unpacked_operation
assert data == unpacked_data

print("*****************************************")
print("***** Done testing wire protocol... *****")
print("*****************************************")

########################################
# Testing the wire protocol chat app
########################################

print("*************************************************")
print("***** Testing the wire protocol chat app... *****")
print("*************************************************")
from wire.chat_service import Chat, User

chat_app = Chat()

# Test creating a user
user1 = User(None)
assert user1.get_name() is None

# Test setting a user's name
user1.set_name("user1")
assert user1.get_name() == "user1"

# Listing the accounts in the chat app
assert chat_app.list_accounts(user1) == [(None, '<server> List of accounts: []')]
assert chat_app.online_users == {}
assert chat_app.accounts == {}

# Adding an account to the chat app
assert chat_app.create_account(user1, "user1") == [(None, '<server> Account "user1" created')]
assert chat_app.online_users == {"user1": None}
assert chat_app.accounts == {"user1": []}

user2 = User(None)
assert chat_app.create_account(user2, "user2") == [(None, '<server> Account "user2" created')]
assert chat_app.online_users == {"user1": None, "user2": None}
assert chat_app.accounts == {"user1": [], "user2": []}

# Listing the accounts in the chat app
assert chat_app.list_accounts(user1) == [(None, '<server> List of accounts: [\'user1\', \'user2\']')]

# Adding an invalid account name to the chat app
assert chat_app.create_account(user1, "y|eet") == [(None, "<server> Username cannot have \" \" or \"|\"")]
assert chat_app.create_account(user1, "y eet") == [(None, "<server> Username cannot have \" \" or \"|\"")]
assert chat_app.create_account(user1, "") == [(None, "<server> Username cannot be empty")]
assert chat_app.online_users == {"user1": None, "user2": None}
assert chat_app.accounts == {"user1": [], "user2": []}

# Logging in to an invalid account in the chat app
assert chat_app.login_account(user1, "notanaccount") == [(None, '<server> Account "notanaccount" not found')]
assert chat_app.online_users == {"user1": None, "user2": None}

# Logging in to an account in the chat app
assert chat_app.login_account(user1, "user1") == [(None, '<server> Logged into "user1"')]
assert chat_app.online_users == {"user1": None, "user2": None}

# Logging out of an account in the chat app
assert chat_app.logout_account(user1) == [(None, '<server> Logged out of "user1"')]
assert chat_app.online_users == {"user2": None}
assert chat_app.accounts == {"user1": [], "user2": []}

# Sending a message in the chat app
assert chat_app.login_account(user1, "user1") == [(None, '<server> Logged into "user1"')]
assert chat_app.send_message(user1, "user2", "Hello, user2!") == [(None, '<user1> Hello, user2!')]

# Sending a message to an invalid account in the chat app
assert chat_app.send_message(user1, "user3", "Hello, user3!") == [(None, '<server> Account "user3" does not exist. Failed to send')]

# Sending a message to an offline account in the chat app
user3 = User(None)
assert chat_app.create_account(user3, "user3") == [(None, '<server> Account "user3" created')]
assert chat_app.logout_account(user3) == [(None, '<server> Logged out of "user3"')]
assert chat_app.send_message(user1, "user3", "Hello, user3!") == [(None, '<server> Account "user3" not online. Message queued to send')]
assert chat_app.accounts == {"user1": [], "user2": [], "user3": ['<user1> Hello, user3!']}

# Getting all queued messages in the chat app
assert chat_app.login_account(user3, "user3") == [(None, '<server> Logged into "user3"')]
assert chat_app.online_users == {"user1": None, "user2": None, "user3": None}
assert chat_app.accounts == {"user1": [], "user2": [], "user3": ['<user1> Hello, user3!']}
assert chat_app.deliver_undelivered(user3) == [(None, '<user1> Hello, user3!')]

# Getting all queued messages in the chat app, except no messages queued
assert chat_app.deliver_undelivered(user3) == [(None, '<server> No messages queued')]
assert chat_app.accounts == {"user1": [], "user2": [], "user3": []}

# Deleting an account in the chat app
assert chat_app.online_users == {"user1": None, "user2": None, "user3": None}
assert chat_app.accounts == {"user1": [], "user2": [], "user3": []}
assert chat_app.delete_account(user1) == [(None, '<server> Account "user1" deleted. You have been logged out')]
assert chat_app.online_users == {"user2": None, "user3": None}
assert chat_app.accounts == {"user2": [], "user3": []}

print("******************************************************")
print("***** Done testing the wire protocol chat app... *****")
print("******************************************************")

########################################
# Testing the GRPC chat app
########################################

print("****************************************")
print("***** Testing the GRPC chat app... *****")
print("****************************************")

from grpc_proto.client import ChatClient
import grpc
import grpc_proto.chat_pb2_grpc as chat_pb2_grpc
from grpc_proto.server import ChatServer
from concurrent import futures

service = ChatServer()

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
chat_pb2_grpc.add_ChatServerServicer_to_server(service, server)
server.add_insecure_port('127.0.0.1:6666')
server.start()

client = ChatClient("127.0.0.1", 6666)


# Test creating a user
assert client.create_account("user1") == "<server> Account created with username \"user1\"."

# Test logging out of a user
assert client.logout_account() == "<server> Account \"user1\" logged out."

# Test sending a message
assert client.create_account("user2") == "<server> Account created with username \"user2\"."
assert client.send_message("user1", "Hello, user1!") == "Message sent."

# Test logging in to a user
assert client.logout_account() == "<server> Account \"user2\" logged out."

# Test getting all queued messages
assert client.login_account("user1") == "<server> Account \"user1\" logged in."
assert client.deliver_undelivered() == "Undelivered messages delivered."

# Test listing all accounts
assert client.list_accounts("") == "<server> All Accounts: [\'user1\', \'user2\']"

# Disconnect the server
service.is_connected = False

time.sleep(0.5)
print("*********************************************")
print("***** Done testing the GRPC chat app... *****")
print("*********************************************")
print("\nAll tests passed!")

