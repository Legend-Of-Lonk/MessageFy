import asyncio
from protocal import *

clients = {}

HISTORY_FILE = "chat_history.txt"


async def save_message(message):
    try:
        with open(HISTORY_FILE, 'a') as f:
            f.write(json.dumps(message) + '\n')
    except Exception as e:
        print(f"Error saving message to history: {e}")


async def send_history(writer, username):
    try:
        with open(HISTORY_FILE, 'r') as f:
            for line in f:
                msg = json.loads(line.strip())
                data = serialize(msg)
                writer.write(data)
                await writer.drain()
        print(f"Sent chat history to {username}")
    except FileNotFoundError:
        print(f"No history file found, starting fresh")
    except Exception as e:
        print(f"Error sending history to {username}: {e}")


async def broadcast(message, exclude=None):
    data = serialize(message)

    for username, (reader, writer) in clients.items():
        if username == exclude:
            continue

        try:
            writer.write(data)
            await writer.drain()
        except Exception as e:
            print(f"Error sending to {username}: {e}")


async def handle_client(reader, writer):
    username = None
    addr = writer.get_extra_info('peername')

    try:
        print(f"New connection")
        data = await reader.readline()
        if not data:
            print(f"Client disconnected before sending JOIN")
            return

        join_msg = deserialize(data)
        if not join_msg or join_msg.get('type') != MSG_JOIN:
            print(f"Invalid JOIN message")
            return

        username = join_msg.get('sender')
        if not username:
            print(f"No username provided")
            return

        print(f"{username} joined")

        clients[username] = (reader, writer)

        await send_history(writer, username)
        join_broadcast = createMessage(
            sender="Server",
            type=MSG_JOIN,
            content=f"{username} has joined the chat"
        )
        await save_message(join_broadcast)
        await broadcast(join_broadcast)

        user_list_msg = createMessage(
            sender="Server",
            type=MSG_USERLIST,
            content=list(clients.keys())
        )
        await broadcast(user_list_msg)

        while True:
            data = await reader.readline()
            if not data:
                break

            msg = deserialize(data)
            if not msg:
                continue

            msg_type = msg.get('type')

            if msg_type == MSG_MESSAGE:
                print(f"{username}: {msg.get('content')}")
                await save_message(msg)
                await broadcast(msg)

            elif msg_type == MSG_LEAVE:
                print(f"{username} is leaving")
                break

    except asyncio.CancelledError:
        print(f"Connection with {username} cancelled")
    except Exception as e:
        print(f"Error with client {username}: {e}")
    finally:
        if username and username in clients:
            del clients[username]
            print(f"{username} disconnected")

            leave_msg = createMessage(
                sender="Server",
                type=MSG_LEAVE,
                content=f"{username} has left the chat"
            )
            await save_message(leave_msg)
            await broadcast(leave_msg)

            user_list_msg = createMessage(
                sender="Server",
                type=MSG_USERLIST,
                content=list(clients.keys())
            )
            await broadcast(user_list_msg)

        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"Error closing connection: {e}")


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

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
