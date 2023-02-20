########################################
# Testing the wire protocol
########################################
from wire_protocol import pack_packet, unpack_packet

operation = 1
data = "Hello, World!"
packet = pack_packet(operation, data)
unpacked_operation, unpacked_data = unpack_packet(packet)

assert operation == unpacked_operation
assert data == unpacked_data


########################################
# Testing the chat app
########################################
from utils import Chat, User

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
assert chat_app.create_account(user1, "user1") == [(None, "<server> Account user1 created")]
assert chat_app.online_users == {"user1": None}
assert chat_app.accounts == {"user1": []}

user2 = User(None)
assert chat_app.create_account(user2, "user2") == [(None, "<server> Account user2 created")]
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
assert chat_app.login_account(user1, "notanaccount") == [(None, "<server> Account notanaccount not found")]
assert chat_app.online_users == {"user1": None, "user2": None}

# Logging in to an account in the chat app
assert chat_app.login_account(user1, "user1") == [(None, "<server> Logged into user1")]
assert chat_app.online_users == {"user1": None, "user2": None}

# Logging out of an account in the chat app
assert chat_app.logout_account(user1) == [(None, '<server> Logged out of user1')]
assert chat_app.online_users == {"user2": None}
assert chat_app.accounts == {"user1": [], "user2": []}

# Sending a message in the chat app
assert chat_app.login_account(user1, "user1") == [(None, "<server> Logged into user1")]
assert chat_app.send_message(user1, "user2", "Hello, user2!") == [(None, '<user1> Hello, user2!')]

# Sending a message to an invalid account in the chat app
assert chat_app.send_message(user1, "user3", "Hello, user3!") == [(None, '<server> Account user3 does not exist. Failed to send')]

# Sending a message to an offline account in the chat app
user3 = User(None)
assert chat_app.create_account(user3, "user3") == [(None, "<server> Account user3 created")]
assert chat_app.logout_account(user3) == [(None, '<server> Logged out of user3')]
assert chat_app.send_message(user1, "user3", "Hello, user3!") == [(None, '<server> Account user3 not online. Message queued to send')]
assert chat_app.accounts == {"user1": [], "user2": [], "user3": ['<user1> Hello, user3!']}

# Getting all queued messages in the chat app
assert chat_app.login_account(user3, "user3") == [(None, '<server> Logged into user3')]
assert chat_app.online_users == {"user1": None, "user2": None, "user3": None}
assert chat_app.accounts == {"user1": [], "user2": [], "user3": ['<user1> Hello, user3!']}
assert chat_app.deliver_undelivered(user3) == [(None, '<user1> Hello, user3!')]

# Getting all queued messages in the chat app, except no messages queued
assert chat_app.deliver_undelivered(user3) == [(None, '<server> No messages queued')]
assert chat_app.accounts == {"user1": [], "user2": [], "user3": []}

# Deleting an account in the chat app
assert chat_app.online_users == {"user1": None, "user2": None, "user3": None}
assert chat_app.accounts == {"user1": [], "user2": [], "user3": []}
assert chat_app.delete_account(user1) == [(None, '<server> Account user1 deleted. You have been logged out')]
assert chat_app.online_users == {"user2": None, "user3": None}
assert chat_app.accounts == {"user2": [], "user3": []}

print("All tests passed!")