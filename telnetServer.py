import asyncio
import websockets

users = {
    "Sparsh": "1234",
    "Srishti": "4321"
}

clients = {}

async def handle_client(websocket, path):
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

    except:
        pass

    finally:
        if username in clients:
            del clients[username]
        await broadcast(f"{username} has left the chat.", username)

async def broadcast(message, sender=None):
    disconnected_clients = []
    for user, ws in clients.items():
        if user != sender:
            try:
                await ws.send(message)
            except:
                disconnected_clients.append(user)

    for user in disconnected_clients:
        del clients[user]

start_server = websockets.serve(handle_client, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
