from __future__ import print_function, division
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import SplineGenerator.SplineGenerator as spline
import time
import sys
import os
from CommunicationScript.MissionPlannerSocket import MissionPlannerSocket, Commands


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
            mp_socket.override_flightplanner_waypoints(parsed_content['waypoints'])
            print("Executed OVERRIDE FLIGHTPLANNER WAYPOINTS")
        elif command == Commands.SYNC_SCRIPT:
            mp_socket.sync_script()
            print("Executed SYNC SCRIPT")
        elif command == Commands.OVERRIDE:
            mp_socket.override_waypoints(parsed_content['waypoints'])
            print("Executed OVERRIDE WAYPOINTS")
        elif command == Commands.TOGGLE_ARM:
            mp_socket.arm_aircraft()
            print("Executed ARM_AIRCRAFT")
        elif command == "CONNECTIP":
            mp_socket.initialise_dronelink(parsed_content['ip'])
            print("Executed CONNECTIP: " + parsed_content['ip'])
        else:
            print("Command received does not exist.")

        # Get the data in a JSON readable format and send it back to whoever asked for it
        self.wfile.write(json.dumps({'statusCode':'200 Command Executed: ' + command}).encode("utf-8"))
        print("Request finished at:", time.ctime())
        

        # Extract list of waypoints
        # parsed_content = json.loads(post_message)
        # waypoint_list = []
        # for waypoint in parsed_content["data"]:
        #     new_waypoint = [waypoint["long"], waypoint["lat"]]
        #     waypoint_list.append(new_waypoint)

        # Get list of Waypoint classes
        # waypoint_class_list = spline.generate_waypoints_from_list(waypoint_list)

        # Create instance of SplineGenerator class
        # spliner = spline.SplineGenerator(
        #     waypoints=waypoint_class_list,
        #     radius_range=(38.1, 39),  # Metres
        #     boundary_points=None,
        #     boundary_resolution=None,
        #     tolerance=0.0,
        #     curve_resolution=3,
        # )

        # Get the data in a JSON readable format and send it back to whoever asked for it
        # waypoint_output_list = spliner.get_waypoint_in_dictionary()
        # self.wfile.write(json.dumps(waypoint_output_list).encode("utf-8"))
        # print("Request finished at:", time.ctime())


if __name__ == "__main__":
    PORT = 8000
    IP = "127.0.0.1"
    server_address = (IP, PORT)
    # MP_HOST = raw_input("Enter IP to connect to: ")
    # print(MP_HOST + type(MP_HOST))
    MP_PORT = 7766
    global mp_socket
    mp_socket = MissionPlannerSocket(MP_PORT)
    server = HTTPServer(server_address, ServerHandler)
    print("Server started on IP address:", IP, "and port:", PORT, "...")

    run_server = True
    awake_check = time.time()
    time_check_interval = 1.0  # Seconds
    while run_server:
        server.handle_request()

    print("Closing server ...")
