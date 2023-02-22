# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import grpc_proto.chat_pb2 as chat__pb2


class ChatServerStub(object):
    """Interface exported by the server.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateAccount = channel.unary_unary(
                '/chatservice.ChatServer/CreateAccount',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.User.FromString,
                )
        self.DeleteAccount = channel.unary_unary(
                '/chatservice.ChatServer/DeleteAccount',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.User.FromString,
                )
        self.ListAccounts = channel.unary_unary(
                '/chatservice.ChatServer/ListAccounts',
                request_serializer=chat__pb2.Wildcard.SerializeToString,
                response_deserializer=chat__pb2.ListofUsernames.FromString,
                )
        self.ChatStream = channel.unary_stream(
                '/chatservice.ChatServer/ChatStream',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.ChatMessage.FromString,
                )
        self.SendMessage = channel.unary_unary(
                '/chatservice.ChatServer/SendMessage',
                request_serializer=chat__pb2.ChatMessage.SerializeToString,
                response_deserializer=chat__pb2.MessageStatus.FromString,
                )
        self.DeliverMessages = channel.unary_unary(
                '/chatservice.ChatServer/DeliverMessages',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.Empty.FromString,
                )
        self.Login = channel.unary_unary(
                '/chatservice.ChatServer/Login',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.User.FromString,
                )
        self.Logout = channel.unary_unary(
                '/chatservice.ChatServer/Logout',
                request_serializer=chat__pb2.User.SerializeToString,
                response_deserializer=chat__pb2.User.FromString,
                )


class ChatServerServicer(object):
    """Interface exported by the server.
    """

    def CreateAccount(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAccount(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListAccounts(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ChatStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeliverMessages(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Logout(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateAccount,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.User.SerializeToString,
            ),
            'DeleteAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAccount,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.User.SerializeToString,
            ),
            'ListAccounts': grpc.unary_unary_rpc_method_handler(
                    servicer.ListAccounts,
                    request_deserializer=chat__pb2.Wildcard.FromString,
                    response_serializer=chat__pb2.ListofUsernames.SerializeToString,
            ),
            'ChatStream': grpc.unary_stream_rpc_method_handler(
                    servicer.ChatStream,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.ChatMessage.SerializeToString,
            ),
            'SendMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMessage,
                    request_deserializer=chat__pb2.ChatMessage.FromString,
                    response_serializer=chat__pb2.MessageStatus.SerializeToString,
            ),
            'DeliverMessages': grpc.unary_unary_rpc_method_handler(
                    servicer.DeliverMessages,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.Empty.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.User.SerializeToString,
            ),
            'Logout': grpc.unary_unary_rpc_method_handler(
                    servicer.Logout,
                    request_deserializer=chat__pb2.User.FromString,
                    response_serializer=chat__pb2.User.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chatservice.ChatServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatServer(object):
    """Interface exported by the server.
    """

    @staticmethod
    def CreateAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatServer/CreateAccount',
            chat__pb2.User.SerializeToString,
            chat__pb2.User.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatServer/DeleteAccount',
            chat__pb2.User.SerializeToString,
            chat__pb2.User.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListAccounts(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatServer/ListAccounts',
            chat__pb2.Wildcard.SerializeToString,
            chat__pb2.ListofUsernames.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ChatStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chatservice.ChatServer/ChatStream',
            chat__pb2.User.SerializeToString,
            chat__pb2.ChatMessage.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatServer/SendMessage',
            chat__pb2.ChatMessage.SerializeToString,
            chat__pb2.MessageStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeliverMessages(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatServer/DeliverMessages',
            chat__pb2.User.SerializeToString,
            chat__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatServer/Login',
            chat__pb2.User.SerializeToString,
            chat__pb2.User.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Logout(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chatservice.ChatServer/Logout',
            chat__pb2.User.SerializeToString,
            chat__pb2.User.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
