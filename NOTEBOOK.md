# Engineering Notebook

## Working Log
### Feb 20th

Tasks done

* Added in working GRPC
    * Decided to create new functions even though the code was very similar in order to handle specifics within GRPC
* Added in authentication checks for when a user tries specific op codes.

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