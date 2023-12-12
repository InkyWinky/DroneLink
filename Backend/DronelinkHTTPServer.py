import threading
import json
import time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from CommunicationScript.MissionPlannerSocket import Commands
from SplineGenerator.SearchPathGenerator import Coord, Polygon
import SplineGenerator.PointToPointPathGenerator as ptpPG
import SplineGenerator.PathGenerator as path_generator
import SplineGenerator.SearchPathGenerator as spliner
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
        self.server = HTTPServer(server_address, ServerHandler)
        self.server.serve_forever()
        print("[TERMINATION] Closed HTTPServerThread")

    def close(self):
        self.server.shutdown()


class ServerHandler(BaseHTTPRequestHandler):
    # Path generator class instance only instantiated once
    path_gen = path_generator.PathGenerator()

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
        content_length = int(self.headers.getheader("content-length", 0))
        post_message = self.rfile.read(content_length)
        statusCode = 200
        message = None
        print('post_message', post_message)
        parsed_content = json.loads(post_message)

        # Run command
        command = parsed_content["command"]

        if command == Commands.PLANE_PARAMETER_UPDATE:
            # Go through each parameter and update it if it is not None
            take_off_point_key = "take_off_point"                           # dict with "lat" and "long"
            do_plot_key = "do_plot"                                         # bool
            minimum_turn_radius_key = "minimum_turn_radius"                 # float in metres
            curve_resolution_key = "curve_resolution"                       # float in waypoints per metre
            altitude_key = "altitude"                                       # float in metres
            search_area_key = "search_area"                                 # list of dicts with "lat "and "long"
            sensor_size_key = "sensor_size"                                 # dict of "width" and "height" each a float in mm
            focal_length_key = "focal_length"                               # float in mm
            paint_overlap_key = "paint_overlap"                             # float
            paint_radius_key = "paint_radius"                               # float in metres
            layer_distance_key = "layer_distance"                           # float in metres
            orientation_key = "orientation"                                 # float in radians
            waypoints_key = "waypoints"                                     # list of dicts with "lat" and "long"
            boundary_points_key = "boundary_points"                         # list of dicts with "lat" and "long"
            boundary_resolution_key = "boundary_resolution"                 # int
            boundary_tolerance_key = "boundary_tolerance"                   # float in metres
            plane_location_key = "plane_location"                           # dict with "lat" and "long"
            plane_bearing_key = "plane_bearing"                             # float in degrees (true bearing)
            target_location_key = "target_location"                         # dict with "lat" and "long"
            target_circle_radius_key = "target_circle_radius"               # float in metres
            minimum_distance_to_start_key = "minimum_distance_to_start"     # float in metres
            times_to_circle_key = "times_to_circle"                         # float

            # Common data
            if take_off_point_key in parsed_content:
                self.path_gen.take_off_point = Coord(lat=parsed_content[take_off_point_key]["lat"], lon=parsed_content[take_off_point_key]["long"])
            if do_plot_key in parsed_content:
                self.path_gen.do_plot = parsed_content[do_plot_key]

            # Common parameters
            if minimum_turn_radius_key in parsed_content:
                self.path_gen.minimum_turn_radius = parsed_content[minimum_turn_radius_key]  # Metres
            if curve_resolution_key in parsed_content:
                self.path_gen.curve_resolution = parsed_content[curve_resolution_key]  # Waypoints per metre on a curve
            if altitude_key in parsed_content:
                self.path_gen.alt = parsed_content[altitude_key]  # Altitude to print plots at

            # Search area specific data
            if search_area_key in parsed_content:
                coord_list = []
                for point in parsed_content[search_area_key]:
                    coord_list.append(Coord(lat=point["lat"], lon=point["long"]))
                self.path_gen.search_area = Polygon(coord_list)

            # Search area specific parameters
            if sensor_size_key in parsed_content:
                width = parsed_content[sensor_size_key]["width"]
                height = parsed_content[sensor_size_key]["height"]
                self.path_gen.sensor_size = (width, height)
            if focal_length_key in parsed_content:
                self.path_gen.focal_length = parsed_content[focal_length_key]
            if paint_overlap_key in parsed_content:
                self.path_gen.paint_overlap = parsed_content[paint_overlap_key]
            if paint_radius_key in parsed_content:
                self.path_gen.paint_radius = parsed_content[paint_radius_key]
            if layer_distance_key in parsed_content:
                self.path_gen.layer_distance = parsed_content[layer_distance_key]
            if orientation_key in parsed_content:
                self.path_gen.orientation = parsed_content[orientation_key]

            # Point-to-point specific data
            if waypoints_key in parsed_content:
                waypoints = []
                for point in parsed_content[waypoints_key]:
                    waypoints.append(ptpPG.Waypoint(x=point["lat"], y=point["long"]))
                self.path_gen.waypoints = waypoints
            if boundary_points_key in parsed_content:
                waypoints = []
                for point in parsed_content[boundary_points_key]:
                    waypoints.append(Coord(lat=point["lat"], lon=point["long"]))
                self.path_gen.boundary_points = waypoints

            # Point-to-point specific parameters
            if boundary_resolution_key in parsed_content:
                self.path_gen.boundary_resolution = parsed_content[boundary_resolution_key]
            if boundary_tolerance_key in parsed_content:
                self.path_gen.boundary_tolerance = parsed_content[boundary_tolerance_key]

            # Target specific parameters
            if plane_location_key in parsed_content:
                self.path_gen.plane_location = Coord(lat=parsed_content[plane_location_key]["lat"], lon=parsed_content[plane_location_key]["long"])
            if plane_bearing_key in parsed_content:
                self.path_gen.plane_bearing = parsed_content[plane_bearing_key]
            if target_location_key in parsed_content:
                self.path_gen.target_location = Coord(lat=parsed_content[target_location_key]["lat"], lon=parsed_content[target_location_key]["long"])
            if target_circle_radius_key in parsed_content:
                self.path_gen.target_circle_radius = parsed_content[target_circle_radius_key]
            if minimum_distance_to_start_key in parsed_content:
                self.path_gen.minimum_distance_to_start = parsed_content[minimum_distance_to_start_key]
            if times_to_circle_key in parsed_content:
                self.path_gen.times_to_circle = parsed_content[times_to_circle_key]

        """Handle the different path generation types"""
        if command == Commands.PATH_GENERATION_SEARCH_AREA:
            self.path_gen.path_generation_type = path_generator.PathGenerationType.SEARCH_AREA
            path_points = self.path_gen.generate_path()
            if path_points is not None:
                mp_sock.override_flightplanner_waypoints(path_points, takeoff_alt=parsed_content['takeoff_alt'], vtol_transition_mode=parsed_content['vtol_transition_mode'])
            else:
                print("Path points are None, no solution found...")
        if command == Commands.PATH_GENERATION_POINT_TO_POINT:
            self.path_gen.path_generation_type = path_generator.PathGenerationType.POINT_TO_POINT
            path_points = self.path_gen.generate_path()
            if path_points is not None:
                mp_sock.override_flightplanner_waypoints(path_points, takeoff_alt=parsed_content['takeoff_alt'], vtol_transition_mode=parsed_content['vtol_transition_mode'])
            else:
                print("Path points are None, no solution found...")
        if command == Commands.PATH_GENERATION_FLY_TO_CIRCLE_TARGET:
            self.path_gen.path_generation_type = path_generator.PathGenerationType.FLY_TO_CIRCLE_TARGET
            path_points = self.path_gen.generate_path()
            if path_points is not None:
                mp_sock.override_flightplanner_waypoints(path_points, takeoff_alt=parsed_content['takeoff_alt'])
            else:
                print("Path points are None, no solution found...")
        if command == Commands.PATH_GENERATION_FLY_TO_TARGET_PAYLOAD:
            self.path_gen.path_generation_type = path_generator.PathGenerationType.FLY_TO_TARGET_PAYLOAD
            path_points = self.path_gen.generate_path()
            if path_points is not None:
                mp_sock.override_flightplanner_waypoints(path_points, do_RTL=True)
            else:
                print("Path points are None, no solution found...")

        if command == Commands.OVERRIDE_FLIGHTPLANNER:
            # Make instance of SearchPathGenerator
            waypoint_spliner = spliner.SearchPathGenerator()
            start_pt = spliner.Coord(parsed_content['waypoints'][0]['lat'], parsed_content['waypoints'][0]['long'])
            # Give arguments
            waypoint_spliner.set_search_area(parsed_content['waypoints'])
            waypoint_spliner.set_parameters(minimum_turn_radius=0.0004,     # The minimum turn radius of the plane
                                            layer_distance=0.001,           # Distance between layers on map. Use this or both focal length and sensor size, not all three
                                            curve_resolution=4,             # How many waypoints per metre for curves
                                            start_point=start_pt,               # Where the plane takes off from. Leave as None if not known
                                            focal_length=None,              # Focal length of the camera on board the plane in mm
                                            sensor_size=None,               # Sensor size of the camera on board the plane as (width, height) in mm
                                            paint_overlap=0.2,               # The percentage of overlap desired for the camera to see on consecutive layers
                                            alt=parsed_content['cruise_alt']                          # Default Alt to set waypoints to
                                            )             

            # Generate and save spline
            waypoint_spliner.generate_search_area_path(do_plot=False)
            splined_waypoints = waypoint_spliner.get_waypoints()  # A list of dictionaries with keys "long", "lat", and "alt" in order of flight
            mp_sock.override_flightplanner_waypoints(splined_waypoints, takeoff_alt=parsed_content['takeoff_alt'], vtol_transition_mode=parsed_content['vtol_transition_mode'], do_RTL=True)
            # mp_socket.override_flightplanner_waypoints(parsed_content['waypoints'], parsed_content['takeoff_alt'])
            print("Executed OVERRIDE FLIGHTPLANNER WAYPOINTS")
        elif command == Commands.DIRECT_WAYPOINTS:
            mp_sock.override_flightplanner_waypoints(parsed_content['waypoints'], takeoff_alt=parsed_content['takeoff_alt'],  vtol_transition_mode=parsed_content['vtol_transition_mode'], do_RTL=True)
        elif command == Commands.SYNC_SCRIPT:
            mp_sock.sync_script()
            print("Executed SYNC SCRIPT")
        elif command == Commands.OVERRIDE:
            mp_sock.override_waypoints(parsed_content['waypoints'], takeoff_alt=parsed_content['takeoff_alt'], vtol_transition_mode=parsed_content['vtol_transition_mode'], do_RTL=True)
            print("Executed OVERRIDE WAYPOINTS")
        elif command == Commands.TOGGLE_ARM:
            mp_sock.toggle_arm_aircraft()
            print("Executed ARM_AIRCRAFT")
        elif command == Commands.TOGGLE_WEATHER_VANING:
            mp_sock.toggle_weather_vaning()
        elif command == Commands.TOGGLE_VISION_DETECTION:
            mp_sock.toggle_vision_detection()
        elif command == "CONNECTIP":
            result = mp_sock.initialise_dronelink(parsed_content['ip'])
            message = "Successfully connected to Mission Planner."
            if not result:
                statusCode = 400
                message = "Could not initialise the connection to Mission Planner."
            print("Executed CONNECTIP: " + parsed_content['ip'])
        elif command =="SMERF":
            mp_sock.send_command_int(1, MUASComponentID.LIFELINE, MUASCommands.LIFELINE, param1=LifelineCommands.SMERF)
        elif command == "NERF":
            mp_sock.send_command_int(1, MUASComponentID.LIFELINE,  MUASCommands.LIFELINE, param1=LifelineCommands.NERF)
        elif command == "DRIP":
            mp_sock.send_command_int(1, MUASComponentID.LIFELINE,  MUASCommands.LIFELINE, param1=LifelineCommands.DRIP)
        # elif command == "DISREGARD_TARGET":
        #     mp_sock.
        else:
            print("Command received does not exist.")

        # Get the data in a JSON readable format and send it back to whoever asked for it
        # self.wfile.write(json.dumps({'statusCode':'200', 'command':'Command Executed: ' + command}).encode("utf-8"))
        # Send headers
        self.send_RESPONSE(statusCode, message=message)
        print("Request finished at:", time.ctime())
