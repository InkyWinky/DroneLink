import threading
import json
import time
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

class WebSocketThread(threading.Thread):
    def __init__(self, host, mp_socket):
        # host: IP of the host to run the server on.
        # mp_socket: The MissionPlannerSocket that talks to Mission Planner.
        threading.Thread.__init__(self)
        self.server = None
        self.live_data_thread = None
        self.host = host
        self.mp_socket = mp_socket
        global clients
        clients = []
        global clientData
        clientData = []


    def run(self):
        self.server = SimpleWebSocketServer(self.host, 8081, WebSocketServer)
        self.live_data_thread = LiveDataThread(self.mp_socket)
        self.live_data_thread.start()
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
            self.live_data_thread.join()
        except:
            pass
        

class WebSocketServer(WebSocket):
    def handleMessage(self):
        for client in clients:
            if client != self:
                client.sendMessage(self.address[0] + u' - ' + self.data)

    def handleConnected(self):
        print('[WEBSOCKET] ', self.address, 'connected')
        for client in clients:
            client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)
        clientData.append({'messagesCount': 0})

    def handleClose(self):
        index = clients.index(self)
        clients.pop(index)
        clientData.pop(index)
        print('[WEBSOCKET] ', self.address, 'closed')
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
                for message in self.mp_socket.messages[clientData[index]['messagesCount']:]:
                    clientData[index]['messagesCount'] = clientData[index]['messagesCount'] + 1
                    messages_to_send.append(message)
                data['messages'] = messages_to_send
                client.sendMessage(json.dumps(data))
                # print('data:',data)
            self.mp_socket.live_data_mutex.release()
            time.sleep(self.data_interval)
        print("[TERMINATION] Closed LiveDataThread")

    def close(self):
        self.quit = True