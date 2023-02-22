import grpc
import grpc_proto.chat_pb2 as chat_pb2
import grpc_proto.chat_pb2_grpc as chat_pb2_grpc
from utils import print_with_prompt

import threading

import re


class ChatClient:
    """Wrapper class to interact with the grpc chat server"""

    def __init__(self, ip_address, port):
        # server_host, server_port = self.__get_server_config_from_file()
        self.__channel = grpc.insecure_channel(f'{ip_address}:{port}')
        self.__stub = chat_pb2_grpc.ChatServerStub(self.__channel)
        self.__user = None
        self.__is_connected = False

        print("<server> Welcome to Chat!")

    def handler(self, op_code: int, content: str = ""):
        """
        Handler function

        Parameters
        ----------
        exp: str, optional
            Regex expression to filter accounts
        """

        try:
            if op_code == 0:
                self.list_accounts(content)
            elif op_code == 1:
                self.create_account(content)
            elif op_code == 2:
                self.login_account(content)
            elif self.is_connected:
                if op_code == 3:
                    self.logout_account()
                elif op_code == 4:
                    self.delete_account()
                elif op_code == 5:
                    match = re.match(r"(\S+)\|((\S| )+)", content)
                    if match:
                        send_user, message = match.group(1), match.group(2)
                        self.send_message(send_user, message)
                    else:
                        print(f"<server> Invalid input: {content}")
                elif op_code == 6:
                    self.deliver_undelivered()
                else:
                    print(f'<server> {op_code} is not a valid operation code.')
            else:
                print("<server> Operation not permitted. You are not logged in.")
        except grpc.RpcError as rpc_error:
            print(
                f"<server> Exception: code={rpc_error.code()} message={rpc_error.details()}")

    @property
    def is_connected(self):
        return self.__is_connected

    @property
    def username(self):
        if not self.__is_connected:
            return None
        return self.__user.username

    def create_account(self, username: str):
        """Connect to the chat server
        Args:
            username: The username to register against the chat server
        """
        response = self.__stub.CreateAccount(chat_pb2.User(username=username))
        self.__user = response
        self.__is_connected = True

        threading.Thread(target=self.check_messages, daemon=True).start()

        print(
            f'<server> Account created with username "{username}".')

        return f'<server> Account created with username "{username}".'

    def delete_account(self):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        self.__stub.DeleteAccount(self.__user)

        print(f'<server> Account "{self.username}" deleted.')

        self.__user = None

        # return statement for unit testing verification
        return f'<server> Account "{self.username}" deleted.'

    def login_account(self, username: str):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        response = self.__stub.Login(chat_pb2.User(username=username))

        print(f'<server> Account "{self.username}" logged in.')

        self.__user = response
        self.__is_connected = True

        # return statement for unit testing verification
        return f'<server> Account "{self.username}" logged in.'

    def logout_account(self):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        self.__stub.Logout(self.__user)
        print(f'<server> Account "{self.username}" logged out.')
        username = self.username
        
        self.__user = None
        self.__is_connected = False

        # return statement for unit testing verification
        return f'<server> Account "{username}" logged out.'

    def list_accounts(self, wildcard: str):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        response = self.__stub.ListAccounts(
            chat_pb2.Wildcard(wildcard=wildcard))

        print(f"<server> All Accounts: {str(response.usernames)}")

        # return statement for unit testing verification
        return f"<server> All Accounts: {str(response.usernames)}"

    def send_message(self, send_user: str, message: str):
        """Send a message to the chat server
        Raises:
            NotConnectedError: Raised when a connection has not been made to the chat server.
        """
        self.__stub.SendMessage(chat_pb2.ChatMessage(username=self.username, recip_username=send_user, message=message))
        
        # return statement for unit testing verification
        return "Message sent."

    def check_messages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        for chat_message in self.__stub.ChatStream(chat_pb2.User(username=self.__user.username)):  # this line will wait for new messages from the server!
            print_with_prompt("<{}> {}".format(chat_message.username,
                  chat_message.message))  # debugging statement

    def deliver_undelivered(self):
        self.__stub.DeliverMessages(self.__user)

        # return statement for unit testing verification
        return "Undelivered messages delivered."
