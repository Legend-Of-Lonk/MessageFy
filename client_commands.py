# -*- coding: utf-8 -*-
def handle_command(command, app):
    if command[0] == '/' and command[1] != '/':
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '/help':
            app.add_system_message("Available commands:")
            app.add_system_message("  /help - Show this help message")
            app.add_system_message("  /clear - Clear your chat display")
            app.add_system_message("  /shrug - Send shrug emoticon")
            return True

        elif cmd == '/clear':
            try:
                chat_display = app.query_one("#chat_messages")
                chat_display.clear()
                app.add_system_message("Chat display cleared")
            except Exception as e:
                app.add_system_message(f"Error clearing display: {e}")
            return True

        elif cmd == '/shrug':
            return r'¯\_(ツ)_/¯'

        else:
            app.add_system_message(f"Unknown command: {cmd}. Type /help for available commands.")
            return True

    return False
