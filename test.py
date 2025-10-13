import asyncio
from protocal import *

async def test_client():
    """
    Simple test client to verify the server works.
    """
    print("Connecting to server...")

    try:
        # Connect to the server
        reader, writer = await asyncio.open_connection('127.0.0.1', 5000)
        print("Connected!")

        # Send JOIN message
        print("\nSending JOIN message...")
        join = createMessage('TestUser', type=MSG_JOIN)
        writer.write(serialize(join))
        await writer.drain()

        # Receive and print any responses (history, join confirmation, user list)
        print("\nReceiving initial messages...")
        for i in range(3):
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=2.0)
                if data:
                    msg = deserialize(data)
                    print(f"  Received: {msg}")
            except asyncio.TimeoutError:
                break

        # Send a test message
        print("\nSending test message...")
        msg = createMessage('TestUser', content='Hello from test client!')
        writer.write(serialize(msg))
        await writer.drain()

        # Receive the echoed message
        print("\nWaiting for message echo...")
        try:
            data = await asyncio.wait_for(reader.readline(), timeout=2.0)
            if data:
                msg = deserialize(data)
                print(f"  Received: {msg}")
        except asyncio.TimeoutError:
            print("  No response (timeout)")

        # Send another message
        print("\nSending another message...")
        msg2 = createMessage('TestUser', content='This is message #2')
        writer.write(serialize(msg2))
        await writer.drain()

        # Receive response
        try:
            data = await asyncio.wait_for(reader.readline(), timeout=2.0)
            if data:
                msg = deserialize(data)
                print(f"  Received: {msg}")
        except asyncio.TimeoutError:
            print("  No response (timeout)")

        # Send LEAVE message
        print("\nSending LEAVE message...")
        leave = createMessage('TestUser', type=MSG_LEAVE)
        writer.write(serialize(leave))
        await writer.drain()

        # Close connection
        print("\nClosing connection...")
        writer.close()
        await writer.wait_closed()
        print("Disconnected!")

    except ConnectionRefusedError:
        print("ERROR: Could not connect to server. Is it running?")
        print("Start the server first with: python3 server.py")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("MessageFy Server Test Client")
    print("=" * 50)
    asyncio.run(test_client())
    print("\nTest complete!")
