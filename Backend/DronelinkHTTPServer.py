import threading
import json
import time
import http.server
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from CommunicationScript.MissionPlannerSocket import Commands
import SplineGenerator.SearchPathGenerator as spliner
import SplineGenerator.PathGenerator as directSpliner
from mav_enums import *

class HTTPServerThread(threading.Thread):
    def __init__(self, host, mp_socket, vision_websocket_url):
        # host: IP of the host to run the server on.
        # mp_socket: The MissionPlannerSocket that talks to Mission Planner.
        # vision_websocket_url: The WebSocket URL for Vision's Server for video feed.
        threading.Thread.__init__(self)
        self.server = None
        self.host = host
        self.mp_socket = mp_socket
        self.vision_websocket_url = vision_websocket_url
        global mp_sock
        mp_sock = mp_socket

    def run(self):
        server_address = (self.host, 8000)
        self.server = http.server.HTTPServer(server_address, ServerHandler)
        self.server.serve_forever()
        print("[TERMINATION] Closed HTTPServerThread")

    def close(self):
        self.server.shutdown()


class ServerHandler(http.server.SimpleHTTPRequestHandler):

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

    def send_RESPONSE(self, statusCode, message=None):
        self.send_response(statusCode, message=message)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Origin, X-Requested-With, Content-Type, Accept",
        )
        self.end_headers()
    def do_POST(self):
        # Get the message from API client
        content_length = int(self.headers.get("content-length", 0))
        post_message = self.rfile.read(content_length)
        statusCode = 200
        message = None
        print('post_message', post_message)
        parsed_content = json.loads(post_message)

        # Run command
        command = parsed_content["command"]
        if command == Commands.OVERRIDE_FLIGHTPLANNER:
            # Make instance of SearchPathGenerator
            waypoint_spliner = spliner.SearchPathGenerator()

            # Give arguments
            waypoint_spliner.set_search_area(parsed_content['waypoints'])
            waypoint_spliner.set_parameters(minimum_turn_radius=0.0004,       # The minimum turn radius of the plane
                                            layer_distance=0.001,            # Distance between layers on map. Use this or both focal length and sensor size, not all three
                                            curve_resolution=4,          # How many waypoints per metre for curves
                                            start_point=None,               # Where the plane takes off from. Leave as None if not known
                                            focal_length=None,              # Focal length of the camera on board the plane in mm
                                            sensor_size=None,               # Sensor size of the camera on board the plane as (width, height) in mm
                                            paint_overlap=0.2)             # The percentage of overlap desired for the camera to see on consecutive layers

            # Generate and save spline
            waypoint_spliner.generate_path()
            splined_waypoints = waypoint_spliner.get_waypoints()  # A list of dictionaries with keys "long", "lat", and "alt" in order of flight
            mp_sock.override_flightplanner_waypoints(splined_waypoints, parsed_content['takeoff_alt'])

            # mp_socket.override_flightplanner_waypoints(parsed_content['waypoints'], parsed_content['takeoff_alt'])
            print("Executed OVERRIDE FLIGHTPLANNER WAYPOINTS")
        elif command == Commands.DIRECT_WAYPOINTS:
            waypoint_spliner=directSpliner.PathGenerator()
            mp_sock.override_flightplanner_waypoints(parsed_content['waypoints'], parsed_content['takeoff_alt'],  parsed_content['vtol_transition_mode'])
        elif command == Commands.SYNC_SCRIPT:
            mp_sock.sync_script()
            print("Executed SYNC SCRIPT")
        elif command == Commands.OVERRIDE:
            mp_sock.override_waypoints(parsed_content['waypoints'], parsed_content['takeoff_alt'], parsed_content['vtol_transition_mode'])
            print("Executed OVERRIDE WAYPOINTS")
        elif command == Commands.TOGGLE_ARM:
            mp_sock.toggle_arm_aircraft()
            print("Executed ARM_AIRCRAFT")
        elif command == Commands.TOGGLE_WEATHER_VAINING:
            mp_sock.toggle_weather_vaining()
        elif command == "CONNECTIP":
            result = mp_sock.initialise_dronelink(parsed_content['ip'])
            message = "Successfully connected to Mission Planner."
            if not result:
                statusCode = 400
                message = "Could not initialise the connection to Mission Planner."
            print("Executed CONNECTIP: " + parsed_content['ip'])
        elif command =="SMERF":
            mp_sock.send_command_int(1, MUASComponentID.LIFELINE, LifelineCommands.SMERF)
        elif command == "NERF":
            mp_sock.send_command_int(1, MUASComponentID.LIFELINE, LifelineCommands.NERF)
        # elif command == "DISREGARD_TARGET":
        #     mp_sock.
        else:
            print("Command received does not exist.")

        # Get the data in a JSON readable format and send it back to whoever asked for it
        # self.wfile.write(json.dumps({'statusCode':'200', 'command':'Command Executed: ' + command}).encode("utf-8"))
        # Send headers
        self.send_RESPONSE(statusCode, message=message)
        print("Request finished at:", time.ctime())