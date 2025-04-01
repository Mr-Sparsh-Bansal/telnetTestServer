import asyncio
import websockets

users = {
    "Sparsh": "1234",
    "Srishti": "4321"
}

clients = {}

async def handle_client(websocket, path):
    username = None
    try:
        await websocket.send("Username: ")
        username = await websocket.recv()

        await websocket.send("Password: ")
        password = await websocket.recv()

        if username not in users or users[username] != password:
            await websocket.send("Invalid credentials. Connection closed.")
            return

        clients[username] = websocket
        await broadcast(f"{username} has joined the chat!", username)

        await websocket.send("Welcome to the chat! Type your message and press Enter.")

        async for message in websocket:
            await broadcast(f"[{username}]: {message}", username)

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        if username and username in clients:
            del clients[username]
        await broadcast(f"{username} has left the chat.", username)

async def broadcast(message, sender=None):
    disconnected_clients = []
    for user, ws in clients.items():
        if user != sender:
            try:
                await ws.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(user)

    for user in disconnected_clients:
        del clients[user]

async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    await server.wait_closed()

# ✅ FIX: Properly create and set a new event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.run_until_complete(main())
loop.run_forever()
