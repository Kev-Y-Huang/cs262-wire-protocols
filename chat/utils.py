from typing import NewType
import re

from _thread import *
import threading

Response = NewType('response', tuple[int, str])


class Chat:
    """
    A class used to handle chat functions
    ...

    Attributes
    ----------
    current_user : str
        the current user

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    def __init__(self):
        # dict object that keeps track of accounts
        # {account1 : ['message1', message2], account2, ...}
        self.accounts = {}
        self.online_users = {}
        self.lock = threading.Lock()

    def handler(self, conn, addr, current_user: str, command: int, user: str = "", message: str = "") -> Response:
        # parse the user input string at the pipe character "|"
        # to get the command
        # if "|" not in input:
        # print("""Invalid input string, please use format <command>|<text>
        #         0| -> list user accounts
        #         1|<username> -> create an account with name username
        #         2|<username> -> login to an account with name username
        #         3| -> delete current account
        #         4|<username>~<text> -> send message to username
        #         5| -> deliver all unsent messages to current user
        #         6| -> close connection to server
        #     """)
        # send to current user (0), send to other user specific (1)
        # pass
        # command, text = input.split("|")

        if command == 0:
            return self.list_accounts(conn)
        elif command == 1:
            if " " in message or "|" in message:
                return (0, "Username cannot have \" \" or \"|\"")
            return self.create_account(conn, addr, message)
        elif command == 2:
            return self.login_account(message)
        elif current_user:
            if command == 3:
                return self.delete_account()
            elif command == 4:
                match = re.match(r"(\S+)\|((\S| )+)", message)
                if match:
                    user, message = match
                    return self.send_message(conn, addr, user, message)
                else:
                    return (0, "Invalid input: {}".format(message))
            elif command == 5:
                return self.deliver_undelivered()
            elif command == 6:
                return self.close_server()
        else:
            return Response(0, "Operation not permitted. You are not logged in.")

    def list_accounts(self, conn, exp: str = "\S*") -> Response:
        """
        Prints out the accounts created to current connected port

        Parameters
        ----------
        exp: str
            Regex expression to filter accounts
        """
        # return all the usernames, which are just the keys to dictionary
        filter = re.compile(exp)
        accounts_to_list = []

        self.lock.acquire()
        for account in self.accounts:
            if filter.match(account):
                accounts_to_list.append(account)
        self.lock.release()

        # sends to current user (0)
        return (conn, str(accounts_to_list))

    def create_account(self, conn, addr, username: str) -> Response:
        """
        Creates an account given a specified username

        Parameters
        ----------
        accounts : dict
            The sound the animal makes (default is None)

        username: str
            Username for the new account
        """
        # if the username is not in accounts, we can create the account
        self.lock.acquire()
        if username not in self.accounts:
            self.accounts[username] = []
            self.online_users[username] = (conn, addr)
            response = (conn, "Account {} created".format(username))
        # otherwise, we will need to reject creating the account
        else:
            response = (conn, "Account {} failed to create. Please select another username".format(username))
        self.lock.release()
        return response


    def login_account(self, current_user: str, username: str) -> Response:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        username: str
            Account username 
        """
        self.lock.acquire()
        # if the username is not in accounts, we cannot log in
        if username not in self.accounts:
            response = (0, "Account {} not found".format(username))
        # otherwise, we will try to log in
        else:
            # if the current user is logged in, we need to log them out
            if current_user in self.online_users:
                del self.online_users[current_user]

            # TODO Figure out how to deal with tying user to current machine
            self.current_user = username
            response = (0, "Logged into account {}".format(username))
        self.lock.release()

        return response

    # TODO implement change for online_users being a dictionary
    def delete_account(self, accounts: dict) -> Response:
        """
        Deletes the current account

        Parameters
        ----------
        None
        """
        if self.current_user not in accounts:
            return (0, "A fatal error has occurred. Account failed to delete".format(deleted_account))

        del accounts[self.current_user]
        self.online_users.remove(self.current_user)
        deleted_account = self.current_user
        self.current_user = None
        return (0, "Account {} deleted. You have been logged out".format(deleted_account))

    def send_message(self, conn, addr, username: str, message: str) -> Response:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        username: str
            Account username 
        """
        # if the username does not exist, we cannot send the message
        if username not in self.accounts:
            return (conn, "Account {} does not exist. Failed to send".format(username))
        else:
            # if the user is online, we can send the message directly
            if username in self.online_users:
                recip_conn = self.online_users[username][0]
                return (recip_conn, message)
            else:
                # if they are not online, we need to queue the message, and then let
                # the current user message know that the messaged is queued to send
                self.accounts[username].append(message)
                return (0, "Account {} not online. Message queued to send".format(username))

    def deliver_undelivered(self) -> Response:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        accounts: dict
            Account username 
        """
        messages = []
        for message in self.accounts[self.current_user]:
            messages.append(message)
        # if there were no queued messages, then the messages string will remain empty
        # and we should send a message to the current conection
        if messages == "":
            return (0, "No meesages queued")
        else:
            return (0, str(messages))

    def close_server(self, online_users: set) -> Response:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        """
        self.online_users.remove(self.current_user)
        return (0, "Connection closed")
