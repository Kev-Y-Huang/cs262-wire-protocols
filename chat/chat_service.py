from typing import NewType
import re

from _thread import *
import threading

Response = NewType('response', tuple[int, str])


class User:
    """
    A class used to handle chat functions
    ...

    Attributes
    ----------
    conn :
        socket for the current user

    username : str
        username of the current user logged-in account

    Methods
    -------
    get_conn()
        Gets the socket connection

    get_name()
        Gets the username of the current account

    set_name(username=None)
        Sets the username of the current account
    """

    def __init__(self, conn, username: str = None):
        self.conn = conn
        self.username = username

    def get_conn(self):
        return self.conn

    def get_name(self):
        return self.username

    def set_name(self, username: str = None):
        self.username = username


class Chat:
    """
    A class used to handle chat functions
    ...

    Attributes
    ----------
    accounts : dict
        dictionary of all accounts

    online_users : dict
        dictionary of online users

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the person object.
        """

        self.accounts = {}
        self.online_users = {}
        self.lock = threading.Lock()

    def handler(self, op_code: int, user: User, content: str = "") -> list[Response]:
        """
        Handler function

        Parameters
        ----------
        exp: str, optional
            Regex expression to filter accounts
        """

        if op_code == 0:
            return self.list_accounts(user, content)
        elif op_code == 1:
            return self.create_account(user, content)
        elif op_code == 2:
            return self.login_account(user, content)
        elif user in self.online_users:
            if op_code == 3:
                return self.logout_account(user)
            elif op_code == 4:
                return self.delete_account(user)
            elif op_code == 5:
                match = re.match(r"(\S+)\|((\S| )+)", content)
                if match:
                    send_user, message = match.group(1), match.group(2)
                    return self.send_message(user, send_user, message)
                else:
                    return [(user.get_conn(), f"<server> Invalid input: {content}")]
            elif op_code == 6:
                return self.deliver_undelivered(user)
        else:
            return [(user.get_conn(), "<server> Operation not permitted. You are not logged in.")]

    def list_accounts(self, user: User, exp: str = "\S*") -> list[Response]:
        """
        Prints out the accounts created to current connected port

        Parameters
        ----------
        exp: str
            Regex expression to filter accounts
        """

        conn = user.get_conn()

        # Checks if the passed-in expression is a valid regex pattern
        try:
            filter = re.compile(exp)
        except:
            return [(conn, f"<server> {exp} is not a valid regex pattern.")]

        accounts_to_list = []

        self.lock.acquire()
        for account in self.accounts:
            if filter.match(account):
                accounts_to_list.append(account)
        self.lock.release()

        return [(conn, f"<server> List of accounts: {str(accounts_to_list)}")]

    def create_account(self, user: User, username: str) -> list[Response]:
        """
        Creates an account given a specified username

        Parameters
        ----------
        accounts : dict
            The sound the animal makes (default is None)

        username: str
            Username for the new account
        """

        conn = user.get_conn()

        # Checks if the passed-in username is valid
        if " " in username or "|" in username:
            return [(conn, "<server> Username cannot have \" \" or \"|\"")]
        
        if "" == username:
            return [(conn, "<server> Username cannot be empty")]

        # if the username already exists, reject the request
        self.lock.acquire()
        if username in self.accounts:
            response = (
                conn, f"<server> Account \"{username}\" failed to create. Please select another username")
        else:
            self.accounts[username] = []
            self.online_users[username] = conn
            user.set_name(username)
            response = (conn, f"<server> Account \"{username}\" created")
        self.lock.release()
        return [response]

    def login_account(self, user: User, username: str) -> list[Response]:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        username: str
            Account username 
        """

        conn = user.get_conn()

        self.lock.acquire()
        # if the username is not in accounts, we cannot log in
        if username not in self.accounts:
            response = (conn, f"<server> Account \"{username}\" not found")
        # otherwise, we will try to log in
        else:
            # if the user is logged-in to a different account, we need to log them out
            if user.get_name() in self.online_users:
                del self.online_users[user.get_name()]

            self.online_users[username] = conn
            user.set_name(username)
            response = (conn, f"<server> Logged into \"{username}\"")
        self.lock.release()

        return [response]

    def logout_account(self, user: User) -> list[Response]:
        """
        Logs the user out of the account given a specified username

        Parameters
        ----------

        username: str
            Account username 
        """

        conn = user.get_conn()
        to_logout = user.get_name()

        if to_logout not in self.accounts or to_logout not in self.online_users:
            return [(conn, f"<server> You are not logged in, or account \"{to_logout}\" does not exist. Failed to logout")]

        self.lock.acquire()
        del self.online_users[user.get_name()]
        self.lock.release()

        user.set_name()
        return [(conn, f"<server> Logged out of \"{to_logout}\"")]

    def delete_account(self, user: User) -> list[Response]:
        """
        Deletes the current account

        Parameters
        ----------
        None
        """

        conn = user.get_conn()
        to_delete = user.get_name()

        self.lock.acquire()
        if to_delete not in self.accounts or to_delete not in self.online_users:
            return [(conn, f"<server> You are not logged in, or account \"{to_delete}\" does not exist. Failed to delete")]
        else:
            del self.accounts[to_delete]
            del self.online_users[to_delete]
        self.lock.release()

        user.set_name()
        return [(conn, f"<server> Account \"{to_delete}\" deleted. You have been logged out")]

    def send_message(self, user: User, send_user: str, message: str) -> list[Response]:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        username: str
            Account username 
        """

        conn = user.get_conn()

        self.lock.acquire()
        # if the username does not exist, we cannot send the message
        if send_user not in self.accounts:
            response = (
                conn, f"<server> Account \"{send_user}\" does not exist. Failed to send")
        else:
            # if the user is online, we can send the message directly
            response_message = f"<{user.get_name()}> {message}"
            if send_user in self.online_users:
                send_conn = self.online_users[send_user]
                response = (send_conn, response_message)
            else:
                # if they are not online, we need to queue the message, and then let
                # the current user message know that the messaged is queued to send
                self.accounts[send_user].append(response_message)
                response = (
                    conn, f"<server> Account \"{send_user}\" not online. Message queued to send")
        self.lock.release()

        return [response]

    def deliver_undelivered(self, user: User) -> list[Response]:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        accounts: dict
            Account username 
        """

        conn = user.get_conn()

        self.lock.acquire()
        responses = [(conn, message)
                     for message in self.accounts[user.get_name()]]
        self.accounts[user.get_name()] = []
        self.lock.release()

        # if there were no queued messages, then the messages string will remain empty
        # and we should send a message to the current conection
        if len(responses) == 0:
            return [(conn, "<server> No messages queued")]
        else:
            return responses
