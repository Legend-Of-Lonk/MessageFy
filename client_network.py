import asyncio
from protocal import *
import time
from client_config import load_server_config


class ChatClient:

    def __init__(self, username, app):
        self.username = username
        self.app = app
        self.reader = None
        self.writer = None
        self.connected = False
        self.loading_history = True
        self.pending_requests = {}
        self.request_counter = 0
        self.intentional_disconnect = False
        self.reconnecting = False

    async def connect(self, host=None, port=None):
        if host is None or port is None:
            host, port = load_server_config()
        try:
            self.reader, self.writer = await asyncio.open_connection(host, port)
            self.connected = True

            join_msg = createMessage(self.username, type=MSG_JOIN)
            self.writer.write(serialize(join_msg))
            await self.writer.drain()

            data = await asyncio.wait_for(self.reader.readline(), timeout=5.0)
            if data:
                msg = deserialize(data)
                if msg:
                    if msg.get('type') == MSG_ERROR:
                        self.connected = False
                        error_content = msg.get('content')
                        self.writer.close()
                        await self.writer.wait_closed()
                        return error_content
                    elif msg.get('type') == MSG_SUCCESS:
                        asyncio.create_task(self.receive_messages())
                        return True

            asyncio.create_task(self.receive_messages())
            return True

        except Exception as e:
            self.connected = False
            self.app.add_system_message(f"Connection failed: {e}")
            return f"Connection failed: {e}"

    async def send_message(self, content):
        if not self.connected:
            return

        try:
            msg = createMessage(self.username, type=MSG_MESSAGE, content=content)
            self.writer.write(serialize(msg))
            await self.writer.drain()
        except Exception as e:
            self.app.add_system_message(f"Error sending message: {e}")

    async def fetch_request(self, type, content):
        if not self.connected:
            return None
        try:
            self.request_counter += 1
            request_id = f"{self.username}_{self.request_counter}"

            future = asyncio.Future()
            self.pending_requests[request_id] = future

            msg = createMessage(self.username, type, content)
            msg['request_id'] = request_id
            self.writer.write(serialize(msg))
            await self.writer.drain()

            result = await asyncio.wait_for(future, timeout=5.0)
            return result
        except asyncio.TimeoutError:
            self.pending_requests.pop(request_id, None)
            self.app.add_system_message("Request timed out")
            return None
        except Exception as e:
            self.pending_requests.pop(request_id, None)
            self.app.add_system_message(f"Error sending request: {e}")
            return None

    async def receive_messages(self):
        try:
            while self.connected:
                data = await self.reader.readline()
                if not data:
                    break

                msg = deserialize(data)
                if not msg:
                    continue

                msg_type = msg.get('type')
                sender = msg.get('sender')
                content = msg.get('content')
                request_id = msg.get('request_id')

                if request_id and request_id in self.pending_requests:
                    future = self.pending_requests.pop(request_id)
                    if not future.done():
                        future.set_result(msg)
                    continue

                if msg_type == MSG_MESSAGE:
                    self.app.add_message(sender, content, loading_history=self.loading_history)
                elif msg_type == MSG_JOIN:
                    self.app.add_system_message(content)
                elif msg_type == MSG_LEAVE:
                    self.app.add_system_message(content)
                elif msg_type == MSG_USERLIST:
                    self.loading_history = False
                    self.app.update_user_list(content)
                elif msg_type == MSG_ERROR:
                    pass

        except Exception as e:
            self.app.add_system_message(f"Connection error: {e}")
        finally:
            if self.intentional_disconnect:
                self.intentional_disconnect = False
                return

            self.connected = False
            self.app.add_system_message("Disconnected from server")

            self.reconnecting = True
            for i in range(5):
                self.app.add_system_message(f"Attempting to reconnect - Attempt {i + 1}/5")
                try:
                    result = await self.connect()
                    if result is True:
                        try:
                            chat_display = self.app.query_one("#chat_messages")
                            chat_display.clear()
                        except Exception:
                            pass
                        self.app.add_system_message("Successfully reconnected to server!")
                        self.reconnecting = False
                        return
                    else:
                        self.app.add_system_message(f"Reconnection failed: {result}")
                except Exception as e:
                    self.app.add_system_message(f"Reconnection attempt failed: {e}")

                if i < 4:
                    await asyncio.sleep(2)

            self.reconnecting = False
            self.app.add_system_message("Failed to reconnect after 5 attempts")

    async def disconnect(self):
        if not self.connected:
            return

        try:
            self.intentional_disconnect = True
            leave_msg = createMessage(self.username, type=MSG_LEAVE)
            self.writer.write(serialize(leave_msg))
            await self.writer.drain()

            self.connected = False
            self.writer.close()
            await self.writer.wait_closed()
        except Exception as e:
            self.app.add_system_message(f"Error disconnecting: {e}")
