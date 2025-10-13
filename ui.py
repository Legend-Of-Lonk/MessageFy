from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog, Static
from textual.containers import Horizontal, Vertical, VerticalScroll


class ChatApp(App):
    CSS_PATH = "style.tcss"
    TITLE = "MessageFy"

    def on_unmount(self) -> None:
        import sys
        sys.stdout.write('\033[?1004l')
        sys.stdout.flush()

    def compose(self) -> ComposeResult:
        with Horizontal(id="main_container"):
            with Vertical(id="chat_container"):
                yield RichLog(id="chat_messages", highlight=True, markup=True, auto_scroll=False, wrap=True)

            with VerticalScroll(id="users_container"):
                yield Static(
                    "Connected Users Appear Here",
                    id="users_list"
                )

        yield Input(placeholder="Type your message here...")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()

        if message:
            chat_display = self.query_one("#chat_messages", RichLog)
            chat_display.write(f"You: {message}")

            event.input.value = ""


def main():
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
