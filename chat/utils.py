from typing import NewType
import re

from _thread import *
import threading

Response = NewType('response', tuple[int, str])

class User:
    def __init__(self, username: str = None):
        self.username = username

    def set_name(self, username: str = None):
        self.username = username

    def get_name(self):
        return self.username

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

    def handler(self, conn, op_code: int, curr_user: User, content: str = "") -> Response:
        """
        Handler function

        Parameters
        ----------
        exp: str, optional
            Regex expression to filter accounts
        """

        if op_code == 0:
            return self.list_accounts(conn, content)
        elif op_code == 1:
            return self.create_account(conn, curr_user, content)
        elif op_code == 2:
            return self.login_account(conn, curr_user, content)
        elif op_code == 3:
            return self.logout_account(conn, curr_user)
        elif op_code == 4:
            return self.delete_account()
        elif op_code == 5:
            match = re.match(r"(\S+)\|((\S| )+)", content)
            if match:
                send_user, message = match.group(1), match.group(2)
                return self.send_message(conn, curr_user, send_user, message)
            else:
                return (conn, f"<server> Invalid input: {content}")
        elif op_code == 6:
            return self.deliver_undelivered()
        else:
            return Response(conn, "<server> Operation not permitted. You are not logged in.")

    def list_accounts(self, conn, exp: str = "\S*") -> Response:
        """
        Prints out the accounts created to current connected port

        Parameters
        ----------
        exp: str
            Regex expression to filter accounts
        """

        # Checks if the passed-in expression is a valid regex pattern
        try:
            filter = re.compile(exp)
        except:
            return (conn, f"<server> {exp} is not a valid regex pattern.")

        accounts_to_list = []

        self.lock.acquire()
        for account in self.accounts:
            if filter.match(account):
                accounts_to_list.append(account)
        self.lock.release()

        return (conn, f"<server> {str(accounts_to_list)}")

    def create_account(self, conn, curr_user: User, username: str) -> Response:
        """
        Creates an account given a specified username

        Parameters
        ----------
        accounts : dict
            The sound the animal makes (default is None)

        username: str
            Username for the new account
        """

        # Checks if the passed-in username is valid
        if " " in username or "|" in username:
            return (conn, "<server> Username cannot have \" \" or \"|\"")

        # if the username already exists, reject the request
        self.lock.acquire()
        if username in self.accounts:
            response = (
                conn, f"<server> Account {username} failed to create. Please select another username")
        else:
            self.accounts[username] = []
            self.online_users[username] = conn
            curr_user.set_name(username)
            response = (conn, f"<server> Account {username} created")
        self.lock.release()
        return response

    def login_account(self, conn, curr_user: User, username: str) -> Response:
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
            response = (conn, f"<server> Account {username} not found")
        # otherwise, we will try to log in
        else:
            # if the user is logged-in to a different account, we need to log them out
            if curr_user.get_name() in self.online_users:
                del self.online_users[curr_user.get_name()]

            self.online_users[username] = conn
            curr_user.set_name(username)
            response = (conn, f"<server> Logged into {username}")
        self.lock.release()

        return response

    def logout_account(self, conn, curr_user: User) -> Response:
        """
        Logs the user out of the account given a specified username

        Parameters
        ----------

        username: str
            Account username 
        """

        self.lock.acquire()
        del self.online_users[curr_user.get_name()]
        self.lock.release()

        logged_out_user = curr_user.get_name()
        curr_user.set_name()

        return (conn, f"<server> Logged out of {logged_out_user}")

    def delete_account(self, conn, curr_user: User, accounts: dict) -> Response:
        """
        Deletes the current account

        Parameters
        ----------
        None
        """

        self.lock.acquire()
        del accounts[curr_user.get_name()]
        del self.online_users[curr_user.get_name()]
        self.lock.release()

        deleted_user = curr_user.get_name()
        curr_user.set_name()

        return (conn, f"<server> Account {deleted_user} deleted. You have been logged out")

    def send_message(self, conn, curr_user: User, send_user: str, message: str) -> Response:
        """
        Logs in to an account given a specified username

        Parameters
        ----------

        username: str
            Account username 
        """

        # if the username does not exist, we cannot send the message
        if send_user not in self.accounts:
            return (conn, f"<server> Account {send_user} does not exist. Failed to send")
        else:
            # if the user is online, we can send the message directly
            if send_user in self.online_users:
                send_conn = self.online_users[send_user]
                return (send_conn, f"<{curr_user.get_name()}> {message}")
            else:
                # if they are not online, we need to queue the message, and then let
                # the current user message know that the messaged is queued to send
                self.accounts[send_user].append(message)
                return (conn, f"<server> Account {send_user} not online. Message queued to send")

    def deliver_undelivered(self, conn) -> Response:
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
            return (conn, "<server> No meesages queued")
        else:
            return (conn, str(messages))
