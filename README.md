# MessageFy

A lightweight, terminal-based chat application built with Python and Textual TUI framework. MessageFy supports real-time messaging for concurrent users with persistent chat history and rich text formatting.

## Features
- Real-time chat
- Rich text formatting
- Persistent message history
- Configurable server connections
- Cross platform (Windows and Linux only right now)
- Terminal based app (works on servers that are console only)

# Installation

## Client

#### &nbsp; Executable

1. Download the latest client from [Releases](https://github.com/Legend-Of-Lonk/MessageFy/releases)
2. Run the navigate to the executable file and run it immediatly close or exit after
3. a server_config.json will appear
```
{
  "host": "127.0.0.0",
  "port": 8080
}
```
4. configure the json for the server you are connecting to
5. run the exe again
6. Enter username 
7. Start chatting

### &nbsp; Python

#### &nbsp; &nbsp; Requirements
  - Python 3.7+
  - Dependencies (see requirements.txt):
    - textual >= 0.47.0
    - rich >= 13.0.0

#### &nbsp; &nbsp; Installation

1. Clone the repository  ``
	 git clone https://github.com/Legend-Of-Lonk/MessageFy.git & 
		cd MessageFy``
2. Install dependencies ``pip install -r requirements.txt``
3. run client.py ``python client.py``
4. a server_config.json will appear
```
{
  "host": "127.0.0.0",
  "port": 8080
}
```
5. configure the json for the server you are connecting to
6. Run client.py again
7. Enter username
8. Start chatting

## Server
>make sure you do all the stuff to port forward 
1. Clone the repository  ``
	 git clone https://github.com/Legend-Of-Lonk/MessageFy.git & 
		cd MessageFy``
2. Install dependencies ``pip install -r requirements.txt``
3. configure server.py to start on the desired port and host
```
async def main():
    import os
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    server = await asyncio.start_server(
        handle_client,
        HOST,
        PORT
    )

    addr = server.sockets[0].getsockname()
    print(f"MessageFy Server started on {addr[0]}:{addr[1]}")
    print("Waiting for connections...")
    print("Type 'help' for server commands\n")

    asyncio.create_task(console_input())

    async with server:
        await server.serve_forever()
```
4. run server.py
5. wait for users :D

## Chatting

MessageFy supports Rich markup for text formatting. See MARKUP_GUIDE.md for full Documentation

## Contribution
Contributions are welcome! Please feel free to submit issues or pull requests



