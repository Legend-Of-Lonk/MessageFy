import asyncio
import json
import os
from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Static
from textual.containers import Horizontal, Vertical, VerticalScroll
from protocal import *


def load_server_config():
    config_file = "server_config.json"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)

    if not os.path.exists(config_path):
        config_path = config_file

    if not os.path.exists(config_path):
        default_config = {
            "host": "shinkansen.proxy.rlwy.net",
            "port": 20565
        }
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created {config_file} with default settings")
        except Exception as e:
            print(f"Warning: Could not create {config_file}: {e}")
            return default_config['host'], default_config['port']

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('host', '127.0.0.1'), config.get('port', 5000)
    except json.JSONDecodeError:
        print(f"Error: {config_file} is not valid JSON. Using defaults (127.0.0.1:5000)")
        return '127.0.0.1', 5000


class ChatClient:
    def __init__(self, username, app):
        self.username = username
        self.app = app
        self.reader = None
        self.writer = None
        self.connected = False

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

                if msg_type == MSG_MESSAGE:
                    self.app.add_message(sender, content)
                elif msg_type == MSG_JOIN:
                    self.app.add_system_message(content)
                elif msg_type == MSG_LEAVE:
                    self.app.add_system_message(content)
                elif msg_type == MSG_USERLIST:
                    self.app.update_user_list(content)
                elif msg_type == MSG_ERROR:
                    pass

        except Exception as e:
            self.app.add_system_message(f"Connection error: {e}")
        finally:
            self.connected = False
            self.app.add_system_message("Disconnected from server")

    async def disconnect(self):
        if not self.connected:
            return

        try:
            leave_msg = createMessage(self.username, type=MSG_LEAVE)
            self.writer.write(serialize(leave_msg))
            await self.writer.drain()

            self.connected = False
            self.writer.close()
            await self.writer.wait_closed()
        except Exception as e:
            self.app.add_system_message(f"Error disconnecting: {e}")


class ChatApp(App):
    CSS_PATH = "style.tcss"
    TITLE = "MessageFy"

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.client = ChatClient(username, self)

    def on_mount(self) -> None:
        asyncio.create_task(self.client.connect())

    def on_unmount(self) -> None:
        import sys
        sys.stdout.write('\033[?1004l')
        sys.stdout.flush()

        if self.client.connected:
            asyncio.create_task(self.client.disconnect())

    def compose(self) -> ComposeResult:
        yield Static("MessageFy", id="header")
        with Horizontal(id="main_container"):
            with Vertical(id="chat_container"):
                yield RichLog(id="chat_messages", highlight=True, markup=True, auto_scroll=True, wrap=True)

            with VerticalScroll(id="users_container"):
                yield Static("No users connected", id="users_list")

        yield Input(placeholder="Type your message here...")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()

        if message:
            asyncio.create_task(self.client.send_message(message))
            event.input.value = ""

    def add_message(self, sender, content):
        from rich.markup import escape
        try:
            chat_display = self.query_one("#chat_messages", RichLog)
            safe_sender = escape(sender)

            if sender == self.username:
                chat_display.write(f"[bold cyan]{safe_sender}[/bold cyan]: {content}")
            else:
                chat_display.write(f"[bold yellow]{safe_sender}[/bold yellow]: {content}")
                self.play_notification_sound()
        except Exception:
            pass

    def play_notification_sound(self):
        try:
            import sys
            if sys.platform == 'win32':
                import winsound
                winsound.Beep(1000, 200)
            else:
                print('\a', end='', flush=True)
        except Exception:
            pass

    def add_system_message(self, content):
        try:
            chat_display = self.query_one("#chat_messages", RichLog)
            chat_display.write(f"[dim italic]{content}[/dim italic]")
        except Exception:
            pass

    def update_user_list(self, users):
        try:
            users_list = self.query_one("#users_list", Static)
            if users:
                user_text = "\n".join([f"• {user}" for user in users])
                users_list.update(f"[bold green]Users ({len(users)})[/bold green]\n\n{user_text}")
            else:
                users_list.update("No users connected")
        except Exception:
            pass


def main():
    import sys
    import time

    host, port = load_server_config()
    print(f"Server: {host}:{port}\n")

    if len(sys.argv) < 2:
        username = input("Enter your username: ").strip()
        if not username:
            print("Username cannot be empty!")
            print("Program will close in 3 seconds...")
            time.sleep(3)
            sys.exit(1)
    else:
        username = sys.argv[1]

    while True:
        print(f"Connecting as '{username}'...")

        try:
            app = ChatApp(username)
            connection_error = [None]

            original_connect = app.client.connect

            async def wrapped_connect(host=None, port=None):
                result = await original_connect(host, port)
                if result != True:
                    connection_error[0] = result
                    app.exit()
                return result

            app.client.connect = wrapped_connect
            app.run()

            if connection_error[0]:
                print(f"\n{connection_error[0]}")
                username = input("Please choose a different username: ").strip()
                if not username:
                    print("Username cannot be empty!")
                    print("Program will close in 3 seconds...")
                    time.sleep(3)
                    sys.exit(1)
                continue
            else:
                break

        except Exception as e:
            print(f"Error: {e}")
            print("Program will close in 5 seconds...")
            time.sleep(5)
            break

    print("Goodbye!")
    time.sleep(1)


if __name__ == "__main__":
    main()
