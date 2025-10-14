import asyncio

def handle_command(command, app):
    if command[0] == '/' and command[1] != '/':
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '/help':
            app.add_system_message("Available commands:")
            app.add_system_message("  /help - Show this help message")
            app.add_system_message("  /clear - Clear your chat display")
            app.add_system_message("  /shrug - Send shrug emoticon")
            app.add_system_message("  /dnd - Toggle Do Not Disturb mode (disable all notifications)")
            app.add_system_message("  /afk - Toggle AFK mode (enable notifications when mentioned)")
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

        elif cmd == '/dnd':
            app.notifications_enabled = not app.notifications_enabled
            if app.notifications_enabled:
                app.add_system_message("[bold green]Do Not Disturb mode disabled[/bold green]")
            else:
                app.afk_mode = False
                app.add_system_message("[bold red]Do Not Disturb mode enabled - all notifications disabled[/bold red]")
            return True

        elif cmd == '/afk':
            import time
            if not app.notifications_enabled:
                app.add_system_message("[bold red]Cannot enable AFK mode - DND is active[/bold red]")
                return True
            app.afk_mode = not app.afk_mode
            if app.afk_mode:
                app.add_system_message("[bold yellow]AFK mode enabled - will notify on mentions[/bold yellow]")
                asyncio.create_task(app.client.send_message("I am AFK"))
            else:
                app.add_system_message("[bold green]AFK mode disabled[/bold green]")
                app.last_activity = time.time()
                asyncio.create_task(app.client.send_message("I am back"))
            return True

        else:
            app.add_system_message(f"Unknown command: {cmd}. Type /help for available commands.")
            return True

    return False
