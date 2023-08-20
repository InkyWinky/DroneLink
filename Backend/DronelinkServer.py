from __future__ import print_function, division
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import threading
import json
import SplineGenerator.SearchPathGenerator as spliner
import time
import socket
import sys
import os
from CommunicationScript.MissionPlannerSocket import MissionPlannerSocket, Commands

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

    def handleClose(self):
       clients.remove(self)
       print('[WEBSOCKET] ', self.address, 'closed')
       for client in clients:
          client.sendMessage(self.address[0] + u' - disconnected')


class ServerHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Origin, X-Requested-With, Content-Type, Accept",
        )
        self.end_headers()

    def do_OPTIONS(self):
        self.do_HEAD()

    def do_POST(self):
        # Send initial headers
        self.do_HEAD()

        # Get the message from API client
        content_length = int(self.headers.getheader("content-length", 0))
        post_message = self.rfile.read(content_length)

        print('post_message', post_message)
        parsed_content = json.loads(post_message)

        # Run command
        command = parsed_content["command"]
        if command == Commands.OVERRIDE_FLIGHTPLANNER:
            # Make instance of SearchPathGenerator
            waypoint_spliner = spliner.SearchPathGenerator()

            # Give arguments
            # waypoint_spliner.set_data(search_area=None)
            # waypoint_spliner.set_parameters(minimum_turn_radius=None,       # The minimum turn radius of the plane
            #                                 layer_distance=None,            # Distance between layers on map. Use this or both focal length and sensor size, not all three
            #                                 curve_resolution=None,          # How many waypoints per metre for curves
            #                                 start_point=None,               # Where the plane takes off from. Leave as None if not known
            #                                 focal_length=None,              # Focal length of the camera on board the plane in mm
            #                                 sensor_size=None,               # Sensor size of the camera on board the plane as (width, height) in mm
            #                                 paint_overlap=None)             # The percentage of overlap desired for the camera to see on consecutive layers

            # # Generate and save spline
            # waypoint_spliner.generate_path()
            # splined_waypoints = waypoint_spliner.get_waypoints()  # A list of dictionaries with keys "long", "lat", and "alt" in order of flight

            mp_socket.override_flightplanner_waypoints(parsed_content['waypoints'])
            print("Executed OVERRIDE FLIGHTPLANNER WAYPOINTS")
        elif command == Commands.SYNC_SCRIPT:
            mp_socket.sync_script()
            print("Executed SYNC SCRIPT")
        elif command == Commands.OVERRIDE:
            mp_socket.override_waypoints(parsed_content['waypoints'])
            print("Executed OVERRIDE WAYPOINTS")
        elif command == Commands.TOGGLE_ARM:
            mp_socket.toggle_arm_aircraft()
            print("Executed ARM_AIRCRAFT")
        elif command == "CONNECTIP":
            mp_socket.initialise_dronelink(parsed_content['ip'])
            print("Executed CONNECTIP: " + parsed_content['ip'])
        else:
            print("Command received does not exist.")

        # Get the data in a JSON readable format and send it back to whoever asked for it
        self.wfile.write(json.dumps({'statusCode':'200', 'command':'Command Executed: ' + command}).encode("utf-8"))
        print("Request finished at:", time.ctime())

class WebSocketThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = None

    def run(self):
        self.server = SimpleWebSocketServer(IP, 8081, WebSocketServer)
        try:
            self.server.serveforever()
        except:
            pass

        print("[TERMINATION] Closed WebSocketThread\n")

    def close(self):
        if self.server is not None:
            self.server.close()


class LiveDataThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.quit = False
        self.data_interval = 1 # second

    def run(self):
        while not self.quit:
            mp_socket.live_data_mutex.acquire()
            data = mp_socket.live_data
            data["ip"] = mp_socket.HOST
            # print("live_data:", data)
            for client in clients:
                client.sendMessage(json.dumps(data))
            mp_socket.live_data_mutex.release()
            time.sleep(self.data_interval)
        print("[TERMINATION] Closed LiveDataThread\n")

    def close(self):
        self.quit = True
        

class HTTPServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = None

    def run(self):
        server_address = (IP, 8000)
        self.server = HTTPServer(server_address, ServerHandler)
        self.server.serve_forever()
        print("[TERMINATION] Closed HTTPServerThread\n")

    def close(self):
        self.server.shutdown()
        


if __name__ == "__main__":

    # Mission Planner Socket
    MP_PORT = 7766
    global mp_socket
    mp_socket = MissionPlannerSocket(MP_PORT)
    print("[INFO] Mission Planner Socket Initialised")

    try:
        hostname = socket.gethostname()
        addr = min(socket.gethostbyname_ex(hostname)[2])
    except Exception:
        addr = "127.0.0.1"
    global IP
    IP = addr

    # Web Socket Server
    global clients
    clients = []
    global web_socket_server
    web_socket_server = WebSocketThread()
    web_socket_server.start()
    print("[INFO] WebSocket Initialised on:", IP + ":" + str(8081))

    # Live Data Sending
    live_data = LiveDataThread()
    live_data.start()
    print("[INFO] Live Data Thread Initialised")

    # HTTP Server
    http_server = HTTPServerThread()
    http_server.start()
    print("[INFO] HTTP Server Initialised on:", IP + ":" + str(8000))

    # web_socket_server.join()
    # live_data.join()
    # http_server.join()
    try:
        a = raw_input("PRESS ENTER TO STOP SERVERS\n")
    finally:
        try:
            web_socket_server.close()
        except:
            pass
        try:
            live_data.close()
        except:
            pass
        try:
            http_server.close()
        except:
            pass
        try:
            mp_socket.close()
        except:
            pass
        
    print("Closing server ...")
