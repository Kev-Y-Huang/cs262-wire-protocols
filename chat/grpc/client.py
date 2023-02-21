import grpc
# import src.utils as utils
import chat_pb2 as chat_pb2
import chat_pb2_grpc as chat_pb2_grpc
# import src.client.exceptions as client_exceptions

import time
import threading

import re
import sys

YAML_CONFIG_PATH = './config.yaml'


class ChatClient:
    """Wrapper class to interact with the grpc chat server"""

    def __init__(self):
        # server_host, server_port = self.__get_server_config_from_file()
        self.__channel = grpc.insecure_channel('localhost:6666')
        self.__stub = chat_pb2_grpc.ChatServerStub(self.__channel)
        self.__user = None
        self.__is_connected = False

        print("<server> Welcome to Chat!")

        if input("Do you already have an account? ") == "yes":
            user_id = int(input("Enter user ID of the account: "))
            username = input("Enter username of the account: ")
            self.login_account(user_id, username)
        else:
            self.create_account(input("Enter username to create account: "))

        while True:
            time.sleep(0.2)
            usr_input = input()
            if usr_input == "q":
                sys.exit()
            else:
                if usr_input != '':
                    # Parses the user input to see if it is a valid input
                    match = re.match(r"(\d)\|((\S| )*)", usr_input)
                    if match:
                        op_code, message = int(match.group(1)), match.group(2)

                        self.handler(op_code, message)

                    else:
                        print(ERROR_MSG)

    def handler(self, op_code: int, content: str = ""):
        """
        Handler function

        Parameters
        ----------
        exp: str, optional
            Regex expression to filter accounts
        """

        if op_code == 0:
            self.list_accounts(content)
        elif op_code == 1:
            self.create_account(content)
        elif op_code == 2:
            match = re.match(r"(\S+)\|(\S+)", content)
            if match:
                user_id, username = match.group(1), match.group(2)
                self.login_account(user_id, username)
            else:
                return [(user.get_conn(), f"<server> Invalid input: {content}")]
        elif op_code == 3:
            self.logout_account()
        elif op_code == 4:
            self.delete_account()
        elif op_code == 5:
            match = re.match(r"(\S+)\|((\S| )+)", content)
            if match:
                send_user, message = match.group(1), match.group(2)
                self.send_message(send_user, message)
            else:
                return [(user.get_conn(), f"<server> Invalid input: {content}")]
        elif op_code == 6:
            return self.deliver_undelivered(user)
        else:
            return [(user.get_conn(), "<server> Operation not permitted. You are not logged in.")]

    # def __get_server_config_from_file(self):
    #     yaml_config = utils.read_yaml_config(YAML_CONFIG_PATH)
    #     return utils.get_server_config_from_yaml(yaml_config)

    @property
    def is_connected(self):
        return self.__is_connected

    @property
    def username(self):
        if not self.__is_connected:
            return None
        return self.__user.username

    @property
    def user_id(self):
        if not self.__is_connected:
            return -1
        return self.__user.user_id

    def create_account(self, name):
        """Connect to the chat server
        Args:
            username: The username to register against the chat server
        """
        response = self.__stub.CreateAccount(chat_pb2.Username(name=name))
        self.__user = response
        self.__is_connected = True

        threading.Thread(target=self.check_messages, daemon=True).start()

        print(
            f"<server> Account created with username {name} and ID {self.__user.user_id}")

        return response

    def delete_account(self):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        if not self.username:
            return True

        self.__stub.DeleteAccount(self.__user)
        self.__user = None
        return True

    def login_account(self, user_id, username):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        response = self.__stub.Login(chat_pb2.User(
            user_id=user_id, username=username))
        self.__user = response
        self.__is_connected = True

        return response

    def logout_account(self):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        if not self.username:
            return True

        self.__stub.Logout(self.__user)
        self.__user = None
        self.__is_connected = False
        return True

    def list_accounts(self, wildcard):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        self.__stub.ListAccounts(wildcard)
        return True

    def subscribe_messages(self):
        """Subscribe against the chat server to recieve new messages
        Raises:
            NotConnectedError: Raised when a connection has not been made to the chat server.
        """
        if not self.__is_connected:
            raise client_exceptions.NotConnectedError(
                "Error: you have not connected to the chat server!")

        return self.__stub.subscribeMessages(self.__user)

    def send_message(self, send_user, message):
        """Send a message to the chat server
        Raises:
            NotConnectedError: Raised when a connection has not been made to the chat server.
        """
        if not self.username:
            raise client_exceptions.NotConnectedError(
                "Error: You are not connected to an active account.")
        return self.__stub.SendMessage(chat_pb2.ChatMessage(username=self.username, recip_username=send_user, message=message))

    def subscribe_active_users(self):
        """Subscribe against the chat server to recieve the active users
        Raises:
            NotConnectedError: Raised when a connection has not been made to the chat server.
        """
        if not self.__is_connected:
            raise client_exceptions.NotConnectedError(
                "Error: you have not connected to the chat server!")
        return self.__stub.subscribeActiveUsers(self.__user)

    def check_messages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        for chat_message in self.__stub.ChatStream(chat_pb2.User(user_id=self.__user.user_id, username=self.__user.username)):  # this line will wait for new messages from the server!
            print("<{}> {}".format(chat_message.username,
                  chat_message.message))  # debugging statement


if __name__ == "__main__":
    c = ChatClient()
