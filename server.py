import asyncio
import websockets
import json

# Store user credentials in Python code
users = {
    "user1": "password1",
    "user2": "password2"
}

clients = {}

async def authenticate(websocket):
    # Request user credentials
    await websocket.send("Enter your User ID: ")
    user_id = await websocket.recv()

    await websocket.send("Enter your Password: ")
    password = await websocket.recv()

    if users.get(user_id) == password:
        await websocket.send(f"Authentication successful. Welcome to the chat room, {user_id}!\n")
        clients[user_id] = websocket
        return user_id
    else:
        await websocket.send("Authentication failed. Closing connection.\n")
        await websocket.close()
        return None

async def chat(websocket, user_id):
    try:
        while True:
            message = await websocket.recv()
            if message.lower() == 'exit':
                await websocket.send(f"You have left the chat room, {user_id}.\n")
                break
            # Broadcast message to all connected clients
            await broadcast(f"{user_id}: {message}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove from clients
        del clients[user_id]
        await broadcast(f"{user_id} has left the chat room.\n")

async def broadcast(message):
    for client in clients.values():
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass

async def main(websocket, path):
    user_id = await authenticate(websocket)
    if user_id:
        await chat(websocket, user_id)

start_server = websockets.serve(main, "0.0.0.0", 8765)

# Run the server
asyncio.get_event_loop().run_until_complete(start_server)
print("Server started on ws://0.0.0.0:8765")
asyncio.get_event_loop().run_forever()
