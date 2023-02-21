import grpc
import chat_pb2 as chat_pb2
import chat_pb2_grpc as chat_pb2_grpc
# import src.client.exceptions as client_exceptions

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
            self.login_account(content)
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
                print(f"<server> Invalid input: {content}")
        elif op_code == 6:
            return self.deliver_undelivered()
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

    def create_account(self, username):
        """Connect to the chat server
        Args:
            username: The username to register against the chat server
        """
        response = self.__stub.CreateAccount(chat_pb2.User(username=username))
        self.__user = response
        self.__is_connected = True

        threading.Thread(target=self.check_messages, daemon=True).start()

        print(
            f"<server> Account created with username {username}")

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

    def login_account(self, username):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        response = self.__stub.Login(chat_pb2.User(username=username))
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

    def list_accounts(self, wildcard: str = "\S*"):
        """Disconnect from the chat server
        Returns:
            boolean: True to indicate the disconnection was successful.
        """
        response = self.__stub.ListAccounts(chat_pb2.Wildcard(wildcard=wildcard))

        print(f"<server> All Accounts: {str(response.usernames)}")

        return True

    def send_message(self, send_user, message):
        """Send a message to the chat server
        Raises:
            NotConnectedError: Raised when a connection has not been made to the chat server.
        """
        if not self.username:
            raise client_exceptions.NotConnectedError(
                "Error: You are not connected to an active account.")
        return self.__stub.SendMessage(chat_pb2.ChatMessage(username=self.username, recip_username=send_user, message=message))

    def check_messages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        for chat_message in self.__stub.ChatStream(chat_pb2.User(username=self.__user.username)):  # this line will wait for new messages from the server!
            print("<{}> {}".format(chat_message.username,
                  chat_message.message))  # debugging statement

    def deliver_undelivered(self):
        self.__stub.DeliverMessages(self.__user)
        return True


if __name__ == "__main__":
    chat = ChatClient()

    while True:
        usr_input = input()
        if usr_input == "quit":
            sys.exit()
        else:
            if usr_input != '':
                # Parses the user input to see if it is a valid input
                match = re.match(r"(\d)\|((\S| )*)", usr_input)
                if match:
                    op_code, message = int(match.group(1)), match.group(2)
                    chat.handler(op_code, message)
                else:
                    print(ERROR_MSG)