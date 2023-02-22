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

        # Checks if the username is valid
        if " " in request.username or "|" in request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Username cannot have " " or "|"')
            return chat_pb2.ListofUsernames()

        # Checks if the username is empty
        if "" == request.username:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Username cannot be empty')
            return chat_pb2.ListofUsernames()

        # Checks if the username is already in use
        if request.username in self.users:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(
                f'"{request.wildcard}" is already in use. Please select another username.')
            return chat_pb2.ListofUsernames()

        # Creates the account
        self.users[request.username] = {"messages": [], "queue": []}
        self.online_users.add(request.username)
        logging.info(f'User "{request.username}" has been created')
        return chat_pb2.User(username=request.username)

    def Login(self, request, context):
        """
        Logs a user into the server
        Returns:
            User: User object
        """
        if request.username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(
                f'No account with and username "{request.username}" found.')
            return chat_pb2.User()

        if request.username in self.online_users:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details(
                f'You cannot login "{request.username}" currently.')
            return chat_pb2.User()

        self.online_users.add(request.username)
        logging.info(f'User has logged into "{request.username}"')
        return chat_pb2.User(username=request.username)

    def Logout(self, request, context):
        """
        Logs a user out of the server
        Returns:
            User: User object
        """
        self.online_users.remove(request.username)
        logging.info(f'User has logged out of "{request.username}"')
        return chat_pb2.User(username=request.username)

    def DeleteAccount(self, request, context):
        '''
        Deletes an account with the given username
        Returns:
            User: User object     
        '''

        if request.username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(
                f'No account found with username "{request.username}".')
            return chat_pb2.User()
        del self.users[request.username]
        self.online_users.remove(request.username)
        logging.info(f'User "{request.username}" has been deleted')
        return chat_pb2.User(username=request.username)

    def SendMessage(self, request, context):
        '''
        Sends a message to a user
        Returns:
            Empty: Empty object
        '''
        # if the username does not exist, we cannot send the message
        if request.username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(
                f'Account {request.username} does not exist. Failed to send.')
            return chat_pb2.Empty()
        else:
            # if the user is online, we can send the message directly
            if request.recip_username in self.online_users:
                self.users[request.recip_username]["messages"].append(request)
                logging.info(f'Message sent to "{request.recip_username}"')
            else:
                # if they are not online, we need to queue the message, and then let
                # the current user message know that the messaged is queued to send
                self.users[request.recip_username]["queue"].append(request)
                logging.info(f'Message queued for "{request.recip_username}"')

        return chat_pb2.Empty()

    def DeliverMessages(self, request, context):
        """
        Delivers all queued messages to the user
        Returns:
            Empty: Empty object
        """
        queue = self.users[request.username]["queue"]
        self.users[request.username]["messages"].extend(queue)
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
            # Send messages to the user if they exist
            while self.users[request.username]["messages"]:
                yield self.users[request.username]["messages"].pop(0)
