''' Example client implementation using websockets'''
import websockets
import asyncio

# create function that is executed when server
async def listen():
    url = "ws://127.0.0.1:7890"

    async with websockets.connect(url) as ws:
        await ws.send("Hello!")
        msg = await ws.recv()
        print(msg)


# control event loop using listen() function
asyncio.get_event_loop().run_until_complete(listen())
asyncio.get_event_loop().run_forever()