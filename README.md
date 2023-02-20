# CS 262 Design Exercise 1: Wire Protocols

## How to run the app

Run `python3 server.py` on the server first, and then `python3 client.py` on the client. 

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