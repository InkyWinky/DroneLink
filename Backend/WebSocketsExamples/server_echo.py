'''Example Simple Echo Server example using WebSockets'''
import websockets
import asyncio

PORT = 7890

async def echo(websocket, path):
    print("[WEBSOCKET] New client connected")
    # websocket: instance of the client
    try:
        async for message in websocket:
            print("[WEBSOCKET] Message received from client: " + message)
            await websocket.send(f"[WEBSOCKET] Response: {message}")
    except websockets.exceptions.ConnectionClosed as e:
        print("[WEBSOCKET] [ERROR] Client disconnected")
        print(e)

        
asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, "localhost", PORT)
)
asyncio.get_event_loop().run_forever()
