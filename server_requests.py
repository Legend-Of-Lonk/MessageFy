from protocal import *

async def handle_fetch_request(clients, msg, username, writer, broadcast):
    msg_type = msg.get('type')
    request_id = msg.get('request_id')

    if msg_type == "FETCH_USER_LIST":
        response = createMessage(
            sender="Server",
            type=MSG_USERLIST,
            content=list(clients.keys())
        )
        if request_id:
            response['request_id'] = request_id

        writer.write(serialize(response))
        await writer.drain()
        print(f"USERLIST sent to {username}")
        return True
    if msg_type == "CHANGE_USERNAME":
        new_name = msg["content"]
        request_id = msg.get('request_id')
        print(f"Changing client's name from {username} to {new_name}")
        if new_name in clients.keys():
            print(f"{new_name} already taken")
            response = createMessage(
                    sender="Server", 
                    type=MSG_ERROR, 
                    content=f"[bold red]{new_name} already taken please try something else [/bold red]"
             )

            if request_id:
                response['request_id'] = request_id

            writer.write(serialize(response))
            await writer.drain()

            return False
        
        clients[new_name] = clients[username]
        del clients[username]

        print(f"{username} succesfully changed to {new_name}")

        response = createMessage(
                sender="Server", 
                type=MSG_SUCCESS, 
                content=f"[bold green]Your name was succesfully changed to {new_name}[/bold green]"
        )

        if request_id:
            response['request_id'] = request_id

        writer.write(serialize(response))
        await writer.drain()

        updated_client_list = createMessage(
                sender="Server",
                type=MSG_USERLIST,
                content=list(clients.keys())
                )
        update_message = createMessage(sender="Server", type=MSG_MESSAGE, content=f"[green]{username} changed their username to {new_name} using /nick")
        await broadcast(updated_client_list)
        await broadcast(update_message)
        

        return new_name

    return False
