import threading
import json
import time
import cv2
import base64
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from sys import platform
import websocket
import rel

class WebSocketThread(threading.Thread):
    def __init__(self, host, mp_socket, vision_websocket_url):
        # host: IP of the host to run the server on.
        # mp_socket: The MissionPlannerSocket that talks to Mission Planner.
        # vision_websocket_url: The WebSocket URL for Vision's Server for video feed.
        threading.Thread.__init__(self)
        self.server = None
        self.live_data_thread = None
        self.host = host
        self.mp_socket = mp_socket
        self.vision_websocket_url = vision_websocket_url
        global clients
        clients = []
        global clientData
        clientData = []


    def run(self):
        self.server = SimpleWebSocketServer(self.host, 8081, WebSocketServer)
        self.live_data_thread = LiveDataThread(self.mp_socket)
        self.fpv_feed_thread = FPVFeedThread()
        self.vision_feed_thread = VisionFeedThread(self.vision_websocket_url)
        self.live_data_thread.start()
        # self.fpv_feed_thread.start()
        self.vision_feed_thread.start()
        try:
            self.server.serveforever()
        except:
            pass

        # self.live_data_thread.join()
        print("[TERMINATION] Closed WebSocketThread")

    def close(self):
        if self.server is not None:
            self.server.close()
        try:
            self.live_data_thread.close()
            self.camera_feed_thread.close()
            self.vision_feed_thread.close()
            self.live_data_thread.join()
            self.camera_feed_thread.join()
            self.vision_feed_thread.join()
        except:
            pass
        

class WebSocketServer(WebSocket):
    def handleMessage(self):
        for client in clients:
            if client != self:
                client.sendMessage(self.address[0] + u' - ' + self.data)

    def handleConnected(self):
        print('[WEBSOCKET] ' + str(self.address) + ' connected')
        for client in clients:
            client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)
        clientData.append({'messagesCount': 0})

    def handleClose(self):
        index = clients.index(self)
        clients.pop(index)
        clientData.pop(index)
        print('[WEBSOCKET] ' + str(self.address) + ' closed')
        for client in clients:
            client.sendMessage(self.address[0] + u' - disconnected')


class LiveDataThread(threading.Thread):
    # Sends Live data taken from Mission Planner to all self.clients connected via WebSockets.
    def __init__(self, mp_socket):
        # clients: The WebSocket clients list
        # mp_socket: The MissionPlannerSocket that talks to Mission Planner.
        threading.Thread.__init__(self)
        self.quit = False
        self.data_interval = 1 # second
        self.mp_socket = mp_socket

    def run(self):
        while not self.quit:
            self.mp_socket.live_data_mutex.acquire()
            data = self.mp_socket.live_data
            data["ip"] = self.mp_socket.HOST
            # print("live_data:", data)
            for index, client in enumerate(clients):
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
                data['ip'] = self.mp_socket.HOST
                data['command'] = "LIVE_DATA"
                client.sendMessage(json.dumps(data))
                # print('data:',data)
            self.mp_socket.live_data_mutex.release()
            time.sleep(self.data_interval)
        print("[TERMINATION] Closed LiveDataThread")

    def close(self):
        self.quit = True

class FPVFeedThread(threading.Thread):
    # Sends Camera Feed Data taken from the onboard camera and other projects to all self.clients connected via WebSockets.
    def __init__(self):
        threading.Thread.__init__(self)
        self.quit = False
        self.camera = None
        self.fps = 5
        

    def run(self):
        while not self.quit:
            # If is no camera, try to connect.
            if not self.camera:
                try:
                    if platform == "win32":
                            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    else:
                            self.camera = cv2.VideoCapture(0)
                    # Set camera resolution
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 1920 / 1280
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 1080 / 720
                    self.camera.set(cv2.CAP_PROP_FPS, 10)
                except:
                    self.camera = None
                time.sleep(2)
            else:
                try:
                    ret, frame = self.camera.read()
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                    # encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 1]
                    buffer = cv2.imencode('.jpg', frame, encode_param)[1]
                    # convert image to base64 before sending
                    data = {"command": "FPV_CAM", "image": "data:image/jpg;base64," + base64.b64encode(buffer)}
                    for index, client in enumerate(clients):
                        client.sendMessage(json.dumps(data))
                except:
                    pass

        print("[TERMINATION] Closed FPVFeedThread")

    def close(self):
        self.quit = True
        self.camera.release()

class VisionFeedThread(threading.Thread):
    # Sends Vision Feed Data taken from the WebSocket relay (Ask Vision) connection and to all self.clients connected via WebSockets.
    def __init__(self, vision_websocket_url):
        threading.Thread.__init__(self)
        self.quit = False
        self.connected = False
        self.vision_websocket_url = vision_websocket_url

    def connect(self):
        self.connected = False
        while not self.connected and not self.quit:
            try:
                self.ws = websocket.create_connection(self.vision_websocket_url)
                self.connected = True
                print("[Vision WebSocket] Successfully Connected")
                break
            except Exception as e:
                self.connected = False
                print("[VISION WebSocket] Failed to connect, retrying...")
            time.sleep(1)

    def run(self):
        
        while not self.quit:
            if not self.connected:
                self.connect()
            try:
                buffer =  self.ws.recv()
                # convert image to base64 before sending
                data = {"command": "VISION_CAM", "image": "data:image/jpg;base64," + base64.b64encode(buffer)}
                for index, client in enumerate(clients):
                    client.sendMessage(json.dumps(data))
            except:
                pass
        self.ws.close()
        print("[TERMINATION] Closed VisionFeedThread")

    def close(self):
        self.quit = True
        
