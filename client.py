import sys
import time
import requests
from client_config import load_server_config
from client_ui import ChatApp

# IMPORTANT: Change this every update
CURRENT_VERSION = "v1.1.1"

def main():
    latest_version = str(requests.get("https://raw.githubusercontent.com/Legend-Of-Lonk/MessageFy/refs/heads/main/version.txt").content).strip().strip("'b\\n")
    if CURRENT_VERSION != latest_version:
        print(f"Version out of date! Running version {CURRENT_VERSION}, and the latest version is {latest_version}.")
        print("Download the new version at https://github.com/Legend-Of-Lonk/MessageFy/releases\n\n")
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
                if result != True and not app.client.reconnecting:
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
