import logging
import re

import grpc
import grpc_proto.chat_pb2 as chat_pb2
import grpc_proto.chat_pb2_grpc as chat_pb2_grpc


class ChatServer(chat_pb2_grpc.ChatServer):
    """
    grpc ChatServer implementation
    ...

    Attributes
    ----------
    users : dict
        dictionary of all accounts

    online_users : set
        set of online users

    is_connected: bool
        Boolean representing whether the server is up and connected

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    def __init__(self):
        # dictionary of all accounts and their messages
        self.users = {}
        # set of online users
        self.online_users = set()
        # boolean representing whether the server is up and connected
        self.is_connected = True

    # helper function to send a message to a user
    def server_message(self, recip_username, message):
        chat_message = {"username": "server", "message": message}
        self.users[recip_username]["messages"].append(chat_message)

    def ListAccounts(self, request, context):
        '''
        Lists an accounts with the given regex pattern
        Returns:
            ListofUsernames: ListofUsernames object  
        '''
        # Checks if the passed-in expression is a valid regex pattern
        try:
            filter = re.compile(request.wildcard)
        except:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(
                f'"{request.wildcard}" is not a valid regex pattern.')
            return chat_pb2.ListofUsernames()

        list_of_usernames = chat_pb2.ListofUsernames()

        for username in self.users:
            if filter.match(username):
                list_of_usernames.usernames.append(username)

        return list_of_usernames

    def CreateAccount(self, request, context):
        '''
        Creates an account with the given username
        Returns:
            User: User object
        '''
        username = request.username

        # Checks if the passed-in username is valid
        if " " in username or "|" in username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Username cannot have " " or "|".')
            return chat_pb2.ListofUsernames()

        # Checks if the username is empty
        if "" == username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Username cannot be empty')
            return chat_pb2.ListofUsernames()

        # Checks if the username is already in use
        if username in self.users:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(
                f'Username "{username}" is already in use.')
            return chat_pb2.ListofUsernames()

        # Updates chat server state for the new account
        self.users[username] = {"messages": [], "queue": []}
        self.online_users.add(username)
        logging.info(f'User "{username}" has been created')
        return chat_pb2.User(username=username)

    def Login(self, request, context):
        """
        Logs a user into the server
        Returns:
            User: User object
        """
        username = request.username

        # Check if the username is not in accounts
        if username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(
                f'Account "{username}" not found.')
            return chat_pb2.User()

        # Check if another user is already logged in
        if username in self.online_users:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details(
                f'You cannot login "{username}" currently.')
            return chat_pb2.User()

        # Updates chat server state with account connection
        self.online_users.add(username)
        logging.info(f'User has logged into "{username}"')
        return chat_pb2.User(username=username)

    def Logout(self, request, context):
        """
        Logs a user out of the server
        Returns:
            User: User object
        """
        username = request.username

        # Checks if the user is logged in
        if username not in self.users or username not in self.online_users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(
                f'You are not logged in, or account "{username}" does not exist.')
            return chat_pb2.User()

        # Deletes the user from the online users
        self.online_users.remove(username)
        logging.info(f'User has logged out of "{username}"')
        return chat_pb2.User(username=username)

    def DeleteAccount(self, request, context):
        '''
        Deletes an account with the given username
        Returns:
            User: User object     
        '''
        username = request.username

        # Checks if the user is logged in or exists
        if username not in self.online_users or username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(
                f'You are not logged in, or account "{username}" does not exist.')
            return chat_pb2.User()

        # Deletes the user from the online users and the users dictionary
        del self.users[username]
        self.online_users.remove(username)
        logging.info(f'User "{username}" has been deleted')
        return chat_pb2.User(username=username)

    def SendMessage(self, request, context):
        '''
        Sends a message to a specified user
        Returns:
            Empty: Empty object
        '''
        recip_username = request.recip_username

        # Check if the username does not exist
        if recip_username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Account {recip_username} does not exist.')
            return chat_pb2.Empty()
        # send the message directly if the user is online
        elif recip_username in self.online_users:
            self.users[recip_username]["messages"].append(request)
            logging.info(f'Message sent to "{recip_username}"')
        # queue the message if the user is not online
        else:
            self.users[recip_username]["queue"].append(request)
            logging.info(f'Message queued for "{recip_username}"')

        return chat_pb2.Empty()

    def DeliverMessages(self, request, context):
        """
        Delivers all queued messages to the user
        Returns:
            Empty: Empty object
        """
        # Dump all queued messages into the user's message list
        queue = self.users[request.username]["queue"]
        self.users[request.username]["messages"].extend(queue)

        # Clear the queue
        self.users[request.username]["queue"] = []
        
        logging.info(f'All queued messages delivered to "{request.username}"')
        return chat_pb2.Empty()

    def ChatStream(self, request, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        logging.info(f'ChatStream initialized for "{request.username}"')

        # If the user is not online, we cannot send them messages
        while self.is_connected and request.username in self.online_users:
            # if there the user has deleted, they will not be in self.users
            # not checking for this may cause a multi-threaded error so we should 
            # stop streaming messages to that user since their account is deleted
            if request.username not in self.users:
                break
            # Send messages to the user if they exist
            while self.users[request.username]["messages"]:
                yield self.users[request.username]["messages"].pop(0)
