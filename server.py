import asyncio
from protocal import *
from server_requests import handle_fetch_request

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

    clients_snapshot = list(clients.items())

    for username, (reader, writer) in clients_snapshot:
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
    authenticated = False

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

        if username in clients:
            print(f"Username '{username}' is already in use, rejecting connection")
            error_msg = createMessage(
                sender="Server",
                type=MSG_ERROR,
                content=f"Username '{username}' is already taken. Please choose a different username."
            )
            writer.write(serialize(error_msg))
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        print(f"{username} joined")

        clients[username] = (reader, writer)
        authenticated = True

        success_msg = createMessage(
            sender="Server",
            type=MSG_SUCCESS,
            content="Connected successfully"
        )
        writer.write(serialize(success_msg))
        await writer.drain()

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
            
            elif msg_type in FETCH_REQUESTS.values() or msg_type in CUSTOM_REQUESTS.values():
                result = await handle_fetch_request(clients, msg, username, writer, broadcast)
                if msg_type == CUSTOM_REQUESTS["CHANGE_USERNAME"] and result != True and result != False:
                    username = result


    except asyncio.CancelledError:
        print(f"Connection with {username} cancelled")
    except Exception as e:
        print(f"Error with client {username}: {e}")
    finally:
        if authenticated and username and username in clients:
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


async def console_input():
    loop = asyncio.get_event_loop()
    while True:
        try:
            cmd = await loop.run_in_executor(None, input)
            if cmd.strip().lower() == "clear":
                try:
                    open(HISTORY_FILE, 'w').close()
                    print("Chat history cleared on server")

                    clear_msg = createMessage(
                        sender="Server",
                        type=MSG_MESSAGE,
                        content="[bold red]Chat history has been cleared by server admin[/bold red]"
                    )
                    await broadcast(clear_msg)
                except Exception as e:
                    print(f"Error clearing history: {e}")
            elif cmd.strip().lower() == "help":
                print("\nServer Commands:")
                print("  clear - Clear chat history and notify all users")
                print("  help  - Show this help message")
                print()
        except Exception as e:
            print(f"Console error: {e}")
            break

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


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
