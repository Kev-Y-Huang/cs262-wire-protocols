# Engineering Notebook

## Key Decisions and Justifications

### Wire Protocol Design

We decided design our wire protocol to use user operation codes to handle user input. We decided to use operation codes because it was a straight forward way to handle user input that was clear to the user. We used the pipe character "|" to separate the operation code from the rest of the user input. An error message would be broadcast to any user that did not input the correct format that specified the correct format to the user, as seen below.

```
Format: <command>|<text>
0|<regex>           -> list user accounts
1|<username>        -> create an account with name username
2|<username>        -> login to an account with name username
3|                  -> logout from current account
4|                  -> delete current account
5|<username>|<text> -> send message to username
6|                  -> deliver all unsent messages to current user
```

The general form of our wire protocol is a 4-byte unsigned integer for the size of the package, the 1-byte unsigned integer for the operation code, followed by a pipe character, followed by the relevant information in each particular request. We encode the whole packet using `utf-8` before sending across a socket. We chose to use `utf-8` because it is the most common encoding used for text, and it is the default encoding for Python. 

We also decided to limit the length of the message to 280 characters. We chose this limit because it seemed like a good idea (thinking Twitter) and we wanted to make sure that the username and message would fit in the 1024 byte buffer we used for our socket and remove any potential edge cases that could arise from having a message that was too long.

### Threading

For both our wire protocol and GRPC implementation, we decided to use threading in the server to handle multiple clients at once. We used locks to ensure that all threads inside of the server could alter the data when one thread was trying to access it. Our server stores all accounts in a dictionary, with each username mapped to the queued messages. We also keep a dictionary of online users, with each username mapped to the socket that the user is connected to. This allowed us to easily check if a user was online or not, and to send messages to the correct socket. Our client runs a continuous loop that takes in user input and sends it to the server. It also runs a separate thread that listens for any messages from the server. This allows the client to continuously listen for messages from the server, and to send messages to the server.

### Testing and handling edge cases

In order to create a robust chat app, we wanted to make sure that all of our code worked as intended. To do this, we wrote tests for all functions within the GRPC and wire protocol chat implementations, as well as the wire protocol we implemented itself. Our tests were able to handle multiple edge cases we thought of, detailed below. In addition to the tests we wrote, we also manually tested to make sure that each of the edge cases below were performing as expected, and also other scenarios like connecting multiple clients to the server, and that the server could handle multiple messages being sent at once.

Edge cases and expected behavior:
* User tries to create an account with a pipe character inside
    * does not allow user to create account
* User tries to create an account with a username that already exists
    * does not allow user to create account
* User tries to create an account with an empty username
    * does not allow user to create account
* User tries to send a message to a user that does not exist
    * does not allow user to send message
* User tries to send a message to themselves
    * allows user to send message to themselves
* User tries to send a message to a user that is not logged in
    * message is queued to be sent to user when they log in
* User tries to send a message to a user that is logged in and has a queued message
    * message is sent to user immediately, queued messages stayed queued
* User tries to log in to an account that is already logged in
    * does not allow new user to log in
* User deletes an account that has queued messages
    * deletes account and all queued messages
    
## Comparing GRPC and Wire Protocol

### Code Complexity

For our GRPC implementation, the code was very similar to the wire protocol implementation. However, most oof the handling was done was split between client side and server side. This decision was made because GRPC automatically generated the functions for the Chat service, so it made sense to just call those functions on the server directly and let GRPC handle the rest. We decided to rewrite the functions inside the GRPC implementation for this reason. However, we tried to share as much common code as possible, while also handling the specifics of GRPC. Future implementations would likely abstract all functions to be shared across both implementations. With our wire protocol, we had to implement the functions ourselves, so we decided to have the client send the op code and the server would handle the rest. The client would send the op code and the server would handle the rest, and then send back a response to the client. Outside of the functions, the code was very similar.

We saw that by using GRPC, our code quality was better, as it allowed us to create specific types and functions for the Chat service. This allowed us to have a more robust implementation of the chat service with more structured calls, data structures, and error messages compared to the wire protocol implementation. However, we saw that the wire protocol implementation easier to test, as we could test the wire protocol and functions directly itself. GRPC is also nice because it is able to be used across languages and can be used to update methods almost instataneously. 

### Performance

For our GRPC implementation, the client was able to continuously stream from the server and receive all messages. When implementing our wire protocol, we saw issues with multiple packets being sent to the client through our wire protocol implementation, specifically when a user decided to deliver all messages that had been queued to send to them when they were offline. Packets were beign skipped when received, even though they were all being sent. We determined this was becauset the packets were being sent to quickly, so to solve this, we decided to add a short timeout between packets being sent.

Sending individual messages across our wire protocol took aroudn 1e-05 seconds, whereas sending a message across GRPC took around 1e-2 seconds. This is likely due to the fact that GRPC is a higher level protocol that handles a lot of the work for us, whereas the wire protocol is a lower level protocol that we have to implement ourselves. We saw that GRPC was more performant than the wire protocol, but we also saw that the wire protocol was easier to implement and test. It is of note that with the timeout we added to our wire protocol implementation, if a user were to send multiple messages with less than 0.1 seconds of each other, he wire protocol woudl be able to send all messages to the client, but it would likely take longer than GRPC.

### Buffer Size

The buffer size were similar. For example, for a message "test" sent across gRPC from user "1" to user "2", gRPC would send a message of size 57 bytes, while the wire protocol would send a message of size 13 bytes. Other combinations of users and messages performed similarly. This is likely due to the fact that gRPC doesn't necessarily have the potential inefficiencies like our wire protocol does. One potential inefficiency in our wire protocol implementation was our use of 4 bytes for the size of packets that could be much smaller. GRPC likely handles this inefficiency for us, and thus we see smaller buffer sizes for it. In addition, we also set a limit of 280 characters for our wire protocol implementation, whereas GRPC does not have this limit since it handles dynamic sizing. 

## Working Log


### Feb 21st

Tasks done

* Bug fixed for GRPC not sending all messages to client
    * adding in lock for when a user is sending messages to another user
* Bug fixed for user trying to log in to an account that is already logged in
* Add response from server when message gets queued/sent immediately for GRPC
* Add response from server when message gets queued/sent immediately for wire protocol
* Add threading locks for GRPC


TODOs

Problems/Questions:


### Feb 20th

Tasks done

* Added in working GRPC
    * Decided to create new functions even though the code was very similar in order to handle specifics within GRPC
* Added in authentication checks for when a user tries specific op codes.
* Added in timeout for wire protocol

TODOs

Problems/Questions:

* We saw issues with multiple packets being sent to the client through our wire protocol implementation, specifically when a user decided to deliver all messages that had been queued to send to them when they were offline. Packets were beign skipped when received, even though they were all being sent. We determined this was becauset the packets were being sent to quickly, so to solve this, we decided to add a short timeout between packets being sent.

### Feb 19th

Tasks done

* Added unit test cases
* Fixed deliver queued messages
    * Should clear all queued messages after they’ve been sent

TODOs

* GRPC

Problems/Questions:

* None

### Feb 18th

Tasks done

* Fixed delete user and logout of account
* Creating a User class
    * Maps username to socket connection
        * Sets usernames
        * Gets socket connection

TODOs

* Implement GRPC

Problems/Questions:

* Error for MacOS using msvcrt
    * Need to check the os of the user and conditionally use msvcrt


### Feb 17th

Tasks done

* Implemented wire protocol
    * Current structure
        * 4 byte unsigned integer for data length (N)
        * 1 byte unsigned integer for operation code
        * N bytes for packet data
    * Format: &lt;command>|&lt;text>
        * 0|                  		-> list user accounts 
        * 1|&lt;username>       	-> create an account with name username 
        * 2|&lt;username>        	-> login to an account with name username 
        * 3|&lt;username>        	-> logout from current account
        * 4|                  		-> delete current account 
        * 5|&lt;username>|&lt;text> 	 -> send message to username 
        * 6|                 		 -> deliver all unsent messages to current user

TODOs

* Optimize code
    * Don’t use busy waiting. Instead, try to use blocking-wait till a descriptor becomes ready.
    * Implement packet size limit and try implement packet breakup

Problems/Questions:


* Why am I getting this error: OSError: [WinError 10038] An operation was attempted on something that is not a socket
    * [Windows can’t use sys.stdin](https://stackoverflow.com/a/35889952)
    * Solution: [Use msvcrt](https://stackoverflow.com/a/46823814)
        * Needed to use msvcrt to manage polling on stdin for windows
        * Needed to add timeout override (currently 0.1 seconds)
* Should we have an op code to disconnect?
    * Right now, we have Ctrl+C to disconnect


### Feb 16th

Tasks done

* Implemented working create account and send message function, creating a Chat class
    * Contains handler function that takes in the op code and then calls each respective function
        * List user accounts
        * Create account
        * Log in to account
        * Log out of account
        * Delete current account
        * Send message to a user name
        * Deliver all unsent messages

TODOs

Problems/Questions:


* Directly sending messages when user is active vs if they are not active and log in later
    * Messages should send immediately if a user is already logged in
* If they are not logged in, then the message should be queued for the user until they login AND send the op code to receive all messages
* Threading
    * Where should we incorporate threading? In the Chat class or the server code
        * Needs to be able to lock every time a user performs an action so that the users/messages are consistent
* Connection vs flags
    * Messages need to be broadcast to specific user
        * Ex. error message to original user, vs message sent to another user
    * Should probably return a tuple with some flag/connection to a user and the message
        * Flag
            * Pros: 
            * Cons: 
        * Connection
            * Pros: will directly get the specific user we need
    * Potentially creating a new User class to handle this?


### Feb 13

Learnings from OH

* Should use op codes
* Should generate uuid key for each account when created
* Delivering should be instantaneous if everyone is logged in
* Or multithreading, need to setup specific firewall rules
    * `sudo ufw allow 2050`
        * This can be any high port number
* Unit testing
    * Simple as create 2 accounts and pass message between the 2
* Wire Protocol
    * Can be simple
    * Doesn’t need a version number
    * Op code should handle each action the client wants to do
    * Can parse the op code with a pipe character or similar character
    * Needs to be sent in bits - not as a whole string

Resources

* [Python Multithreading Tutorial](https://www.geeksforgeeks.org/socket-programming-multi-threading-python/)

### Feb 10

Tasks done

* Implemented basic client-side/server-side code
* Implemented wire protocol
    * Current structure
        * 4 byte unsigned integer for packet length (M)
        * 4 byte unsigned integer for version number
        * 4 byte unsigned integer for data length (N)
        * 1 byte unsigned integer for operation code
        * N bytes for packet data
    * Wire protocol will pack the message user sends in the above format and send from client to server
        * Question: how will we parse the op code, what does the op code actually do?
    * Server will unpack the message received from the client and broadcast to another user

TODOs

* Optimize code
    * Don’t use busy waiting. Instead, try to use blocking-wait till a descriptor becomes ready.
    * Implement packet size limit and try implement packet breakup

Problems/Questions:

* Why am I getting this error: OSError: [WinError 10038] An operation was attempted on something that is not a socket
    * [Windows can’t use sys.stdin](https://stackoverflow.com/a/35889952)

Resources:

* [Simple Chat Room Guide](https://www.geeksforgeeks.org/simple-chat-room-using-python/)
    * Insight into how to continuously communicate between client and server
* [Github example of server-client communication](https://github.com/furas/python-examples/tree/master/socket/simple-protocol)

### Feb. 3rd

* Starting our Wire Protocol
* Choosing to use Python
* Potentially using AWS vs local?
    * AWS
        * Pros: could be run easily on multiple OS/machines
        * Cons: set up time?
    * Local
        * Pros: easier to set up
        * Cons: only one machine can run the server
    * We decided to use local for now