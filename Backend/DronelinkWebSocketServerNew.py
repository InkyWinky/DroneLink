import json
import time
import cv2
import base64
import websockets
import asyncio
from sys import platform
import rel


class WebSocketThread():

    def __init__(self, host, mp_socket, vision_websocket_url, loop):
        # host: IP of the host to run the server on.
        # mp_socket: The MissionPlannerSocket that talks to Mission Planner.
        # vision_websocket_url: The WebSocket URL for Vision's Server for video feed.
        # loop: the current asyncio event loop
        self.live_data_thread = None
        self.host = host
        self.mp_socket = mp_socket
        self.vision_websocket_url = vision_websocket_url
        self.loop = loop 
        global clients
        clients = set()
        global clientData
        clientData = []

            
    async def run(self):
        print(f"[RUNNING] Running WebSocketThread")
        # establish websocket server
        await websockets.serve(self.handler, self.host, 8081)

        # initialise threads
        self.live_data_thread = LiveDataThread(self.mp_socket)
        self.fpv_feed_thread = FPVFeedThread()
        self.vision_feed_thread = VisionFeedThread(self.vision_websocket_url)

        # run threads
        await self.live_data_thread.run()
        await self.vision_feed_thread.run()

        print("[TERMINATION] Closed WebSocketThread")

    async def handler(self, websocket, path):
        clients.add(websocket)
        clientData.append({'messagesCount': 0})
        print(f"[WEBSOCKET] Websocket {websocket} opened")
        # websocket: instance of the client
        try:
            async for message in websocket:
                print(f"[WEBSOCKET] Message received from client: {message}")
                await websocket.send(f"[WEBSOCKET] Response: {message}")
        finally:
            index = clients.index(websocket)
            clients.remove(websocket)
            print(f"[WEBSOCKET] Websocket {websocket} closed")
            clientData.pop(index)

    async def close(self):
        await websockets.close()

class LiveDataThread():
    # Sends Live data taken from Mission Planner to all self.clients connected via WebSockets.
    def __init__(self, mp_socket):
        # clients: The WebSocket clients list
        # mp_socket: The MissionPlannerSocket that talks to Mission Planner.
        self.quit = False
        self.data_interval = 1 # second
        self.mp_socket = mp_socket

    async def run(self):
        print(f"[RUNNING] Running LiveDataThread.run()")
        while not self.quit:
            data = self.mp_socket.live_data
            data["ip"] = self.mp_socket.HOST
            # print("live_data:", data)
            for index, client in enumerate(clients):
                print(f"[RUNNING] Sending message to client {client}")
                messages_to_send = []
                # print(self.clientData[index]['messagesCount'])
                # Send messages to keep client up to date. If the difference is more than 200, send the latest 200 only
                if len(self.mp_socket.messages) - clientData[index]['messagesCount'] > 200:
                    message_index_to_send_from = len(self.mp_socket.messages) - 200
                else:
                    message_index_to_send_from = clientData[index]['messagesCount']
                messages_to_send = self.mp_socket.messages[message_index_to_send_from:]
                clientData[index]['messagesCount'] = len(self.mp_socket.messages)
                # for message in self.mp_socket.messages[clientData[index]['messagesCount']:]:
                #     clientData[index]['messagesCount'] = clientData[index]['messagesCount'] + 1
                #     messages_to_send.append(message)
                data['messages'] = messages_to_send
                data['command'] = "LIVE_DATA"
                
                await client.send(json.dumps(data))
                # print(f'data: {data}')

            asyncio.sleep(self.data_interval)
        print("[TERMINATION] Closed LiveDataThread")

    async def close(self):
        self.quit = True

class FPVFeedThread():
    # Sends Camera Feed Data taken from the onboard camera and other projects to all self.clients connected via WebSockets.
    def __init__(self):
        self.quit = False
        self.camera = None
        self.fps = 5

        self.loop = asyncio.get_event_loop()
        

    async def run(self):
        print(f"[RUNNING] Running FPVFeedThread.run()")
        while not self.quit:
            # If is no camera, try to connect.
            if not self.camera:
                try:
                    if platform == "win32":
                            self.camera = await cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    else:
                            self.camera = await cv2.VideoCapture(0)
                    # Set camera resolution
                    await self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 1920 / 1280
                    await self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 1080 / 720
                    await self.camera.set(cv2.CAP_PROP_FPS, 10)
                except:
                    self.camera = None
                asyncio.sleep(2)
            else:
                try:
                    ret, frame = await self.camera.read()
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                    # encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 1]
                    buffer = await cv2.imencode('.jpg', frame, encode_param)[1]
                    # convert image to base64 before sending
                    data = {"command": "FPV_CAM", "image": "data:image/jpg;base64," + base64.b64encode(buffer)}
                    for index, client in enumerate(clients):
                        await client.send(json.dumps(data))
                except:
                    pass

        print("[TERMINATION] Closed FPVFeedThread")

    async def close(self):
        self.quit = True
        await self.camera.release()

class VisionFeedThread():
    # Sends Vision Feed Data taken from the WebSocket relay (Ask Vision) connection and to all self.clients connected via WebSockets.
    def __init__(self, vision_websocket_url):
        self.quit = False
        self.connected = False
        self.vision_websocket_url = vision_websocket_url

    async def connect(self):
        self.connected = False
        while not self.connected and not self.quit:
            try:
                async with websockets.connect(self.vision_websocket_url) as ws:
                    self.connected = True
                    await ws.send(f"[Vision WebSocket] Successfully Connected")
                break
            except Exception as e:
                self.connected = False
                print("[VISION WebSocket] Failed to connect, retrying...")
            asyncio.sleep(1)

    async def run(self):
        while not self.quit:
            while not self.connected:
                try:
                    self.ws = await websockets.connect(self.vision_websocket_url)
                    self.connected = True
                    await self.ws.send(f"[Vision WebSocket] Successfully Connected")
                except Exception as e:
                    self.connected = False
                    print("[VISION WebSocket] Failed to connect, retrying...")
                asyncio.sleep(1) 

            try:
                buffer = await self.ws.recv()
                # convert image to base64 before sending
                data = {"command": "VISION_CAM", "image": "data:image/jpg;base64," + await base64.b64encode(buffer)}
                for index, client in enumerate(clients):
                    await client.send(json.dumps(data))
            except:
                pass
        await self.ws.close()
        print("[TERMINATION] Closed VisionFeedThread")

    def close(self):
        self.quit = True