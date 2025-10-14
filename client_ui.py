import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Static
from textual.containers import Horizontal, Vertical, VerticalScroll
from client_network import ChatClient
from client_commands import handle_command


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
            result = handle_command(message, self)
            if result is True:
                event.input.value = ""
            elif result is False:
                asyncio.create_task(self.client.send_message(message))
                event.input.value = ""
            else:
                asyncio.create_task(self.client.send_message(result))
                event.input.value = ""

    def _highlight_mention(self, match):
        mentioned_user = match.group(1)
        if mentioned_user == self.username:
            return f"[black on yellow]@{mentioned_user}[/black on yellow]"
        return match.group(0)

    def add_message(self, sender, content):
        from rich.markup import escape
        import re
        try:
            chat_display = self.query_one("#chat_messages", RichLog)
            safe_sender = escape(sender)

            is_mentioned = f"@{self.username}" in content

            if is_mentioned:
                content = re.sub(r'@(\w+)', self._highlight_mention, content)

            if sender == self.username:
                chat_display.write(f"[bold cyan]{safe_sender}[/bold cyan]: {content}")
            else:
                chat_display.write(f"[bold yellow]{safe_sender}[/bold yellow]: {content}")
                if is_mentioned:
                    self.play_notification_sound()
                else:
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
