import logging
import GRPC.chat_pb2 as chat_pb2
import GRPC.chat_pb2_grpc as chat_pb2_grpc
import grpc
import re
from hashlib import md5

from concurrent import futures

class ChatServer(chat_pb2_grpc.ChatServer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self):
        self.users = {}
        self.online_users = set()
        self.is_connected = True

    def CreateAccount(self, request, context):
        if request.username in self.users:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'"{request.wildcard}" is not a valid regex pattern.')
            return chat_pb2.ListofUsernames()
        self.users[request.username] = {"messages": [], "queue": []}
        self.online_users.add(request.username)
        logging.info(f'User {request.username} has be created')
        return chat_pb2.User(username=request.username)

    def DeleteAccount(self, request, context):
        # Checks if the passed-in expression is a valid regex pattern
        if self.users[request.username] != request.user_id: # TODO deal with non existence of user_id
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f'Account {request.username} failed to create. Please select another username.')
            return chat_pb2.User()
        del self.users[request.username]
        self.online_users.remove(request.username)
        logging.info(f'User "{request.username}" has been deleted')
        return chat_pb2.User(username=request.username)

    def ListAccounts(self, request, context):
        # Checks if the passed-in expression is a valid regex pattern
        # try:
        #     filter = re.compile(request.wildcard)
        # except:
        #     context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        #     context.set_details(f'"{request.wildcard}" is not a valid regex pattern.')
        #     return chat_pb2.ListofUsernames()

        list_of_usernames = chat_pb2.ListofUsernames()

        for username in self.users:
            # if filter.match(username):
            list_of_usernames.usernames.append(username)

        return list_of_usernames

    def SendMessage(self, request, context):
        # if the username does not exist, we cannot send the message
        if request.username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Account {request.username} does not exist. Failed to send.')
            return chat_pb2.Empty()
        else:
            # if the user is online, we can send the message directly
            if request.recip_username in self.online_users:
                self.users[request.recip_username]["messages"].append(request)

            #     send_conn = self.online_users[send_user]
            #     response = (send_conn, response_message)
            else:
                # if they are not online, we need to queue the message, and then let
                # the current user message know that the messaged is queued to send
                self.users[request.recip_username]["queue"].append(request)

        return chat_pb2.Empty()
    
    def ChatStream(self, request, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        
        while self.is_connected:
            if request.username in self.online_users and self.users[request.username]["messages"]:
                yield self.users[request.username]["messages"].pop(0)

    def DeliverMessages(self, request, context):
        queue = self.users[request.username]["queue"]
        self.users[request.username]["messages"].extend(queue)
        self.users[request.username]["queue"] = []
        return chat_pb2.Empty()

    def Login(self, request, context):
        if request.username not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'No account with user id {request.user_id} and username {request.username} found')
            return chat_pb2.User()
        
        self.online_users.add(request.username)
        logging.info(f'User has logged into "{request.username}"')
        return chat_pb2.User(username=request.username)

    def Logout(self, request, context):
        self.online_users.remove(request.username)
        logging.info(f'User has logged out of "{request.username}"')
        return chat_pb2.User(username=request.username)


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)-15s]: %(message)s', level=logging.INFO)

    service = ChatServer()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServerServicer_to_server(service, server)

    logging.info('Starting Server')
    server.add_insecure_port(f'localhost:6666')
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info('Stopping Server')
        service.is_connected = False