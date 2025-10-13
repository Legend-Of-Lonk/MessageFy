import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Static
from textual.containers import Horizontal, Vertical, VerticalScroll
from protocal import *


class ChatClient:
    def __init__(self, username, app):
        self.username = username
        self.app = app
        self.reader = None
        self.writer = None
        self.connected = False

    async def connect(self, host='shinkansen.proxy.rlwy.net', port=20565):
        try:
            self.reader, self.writer = await asyncio.open_connection(host, port)
            self.connected = True

            join_msg = createMessage(self.username, type=MSG_JOIN)
            self.writer.write(serialize(join_msg))
            await self.writer.drain()

            asyncio.create_task(self.receive_messages())

            return True
        except Exception as e:
            self.app.add_system_message(f"Connection failed: {e}")
            return False

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

    if len(sys.argv) < 2:
        username = input("Enter your username: ").strip()
        if not username:
            print("Username cannot be empty!")
            print("Program will close in 3 seconds...")
            time.sleep(3)
            sys.exit(1)
    else:
        username = sys.argv[1]

    try:
        app = ChatApp(username)
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Program will close in 5 seconds...")
        time.sleep(5)
    finally:
        print("Goodbye!")
        time.sleep(1)


if __name__ == "__main__":
    main()
