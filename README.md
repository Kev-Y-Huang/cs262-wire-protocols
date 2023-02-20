# CS 262 Design Exercise 1: Wire Protocols

## Description

This is a chat application that we designed for CS262 using wire protocols.

## Setup

Installations you may need:

Ensure that protoc is installed with
```
protoc --version
```

## Built on

We built a server and client using the `socket` and `threading` native Python libraries.

## How to run the app

Navigate into the `chat` folder and run `python3 server.py` on the server first, and  navigate into the `chat` folder and run `python3 client.py` on the client. 

After the client has connected to the server, type in a command in the client terminal, following the commands below.

### Commands for the client

All messages sent by the client be an op code followed by the pipe "|" character.

```
Format: <command>|<text>
0|                  -> list user accounts
1|<username>        -> create an account with name username
2|<username>        -> login to an account with name username
3|<username>        -> logout from current account
4|                  -> delete current account
5|<username>|<text> -> send message to username
6|                  -> deliver all unsent messages to current user
```

### Disconnecting the client

To shut down the client, type `Ctrl+C` in the client terminal. 

## Folder Structure

.
├── chat	                # All of the code is here
|   ├── __init__.py		    # Initializes application from config file
│   ├── chat.proto          # Definition of Protocol Buffer Objects
│   ├── client.py           # Contains the code for the client
│   ├── server.py           # Contains the code for the server
│   ├── wire_protocol.py    # Contains the code for defining the wire protocol
|   ├── tests.py	        # Unit tests for the application
|   └── utils.py		    # Defines the classes (User, Chat) used by the client and server
├── .gitignore	
├── NOTEBOOK.md             # Engineering notebook	
└── README.md