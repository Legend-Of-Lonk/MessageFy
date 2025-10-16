import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Static
from textual.containers import Horizontal, Vertical, VerticalScroll
from client_network import ChatClient
from client_commands import handle_command
from notifypy import Notify


class ChatApp(App):

    CSS_PATH = "style.tcss"
    TITLE = "MessageFy"

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.client = ChatClient(username, self)
        self.notifications_enabled = True
        self.afk_mode = False
        self.last_activity = None
        self.afk_timer_task = None

    def on_mount(self) -> None:
        import time
        self.last_activity = time.time()
        asyncio.create_task(self.client.connect())
        self.afk_timer_task = asyncio.create_task(self.check_afk_timer())

    def on_unmount(self) -> None:
        import sys
        sys.stdout.write('\033[?1004l')
        sys.stdout.flush()

        if self.afk_timer_task:
            self.afk_timer_task.cancel()

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
        import time
        self.last_activity = time.time()

        message = event.value.strip()

        if len(message) > 500:
            self.add_system_message("Message greator than 500 charecters please shorten it")
            return

        if message:
            asyncio.create_task(self._handle_input(message, event.input))

    async def _handle_input(self, message, input_widget):
        result = await handle_command(message, self)
        if result is True:
            input_widget.value = ""
        elif result is False:
            await self.client.send_message(message)
            input_widget.value = ""
        else:
            await self.client.send_message(result)
            input_widget.value = ""

    def _highlight_mention(self, match):
        mentioned_user = match.group(1)
        if mentioned_user == self.username:
            return f"[black on bright_cyan]@{mentioned_user}[/black on bright_cyan]"
        return f"[black on orange1]@{mentioned_user}[/black on orange1]"

    def add_message(self, sender, content, loading_history=False):
        from rich.markup import escape
        import re
        try:
            chat_display = self.query_one("#chat_messages", RichLog)
            safe_sender = escape(sender)

            is_mentioned = f"@{self.username}" in content

            content = re.sub(r'@(\w+)', self._highlight_mention, content)

            if sender == self.username:
                chat_display.write(f"[bold cyan]{safe_sender}[/bold cyan]: {content}")
            else:
                chat_display.write(f"[bold yellow]{safe_sender}[/bold yellow]: {content}")
                if is_mentioned and not loading_history and self.afk_mode:
                    self.send_desktop_notification(sender, content, mentioned=True)
        except Exception:
            pass

    def send_desktop_notification(self, sender, content, mentioned=False):
        if not self.notifications_enabled:
            return

        try:
            notification = Notify()
            notification.application_name = "MessageFy"

            if mentioned:
                notification.title = f"{sender} mentioned you!"
                truncated_content = content[:100] + "..." if len(content) > 100 else content
                notification.message = truncated_content
            else:
                notification.title = f"New message from {sender}"
                truncated_content = content[:100] + "..." if len(content) > 100 else content
                notification.message = truncated_content

            notification.send()
        except:
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

    async def check_afk_timer(self):
        import time
        while True:
            try:
                await asyncio.sleep(10)
                if self.last_activity and not self.afk_mode:
                    elapsed = time.time() - self.last_activity
                    if elapsed >= 300:
                        self.afk_mode = True
                        self.add_system_message("[bold yellow]Auto AFK mode enabled - 5 minutes of inactivity[/bold yellow]")
                        await self.client.send_message("I am AFK")
            except asyncio.CancelledError:
                break
            except Exception:
                pass
