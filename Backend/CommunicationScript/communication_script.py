"""
Mission Planner Communication Script
Creates a communication link between the Backend Server and Mission Planner.
Utilises MavLink and is run as a Mission Planner Script.

Script Usage
From Mission Planner Home, navigate to "Simulation" -> "Plane" -> "Stable".
On the left side, navigate to "Scripts" -> "Select Script" -> "Upload" ->
-> "Run Script"

When developing in the communication script, there are 3 main exposed classes that Mission Planner explicitly sets:
    1. MAV
    Alias for 'MissionPlanner.MainV2.comPort'
    This class exposes the MAVLinkInterface that allows for us to use mavlink functions.
    e.g. 'MAV.doARM(...)' will arm or disarm the vehicle.
    
    2. cs (a.k.a current state)
    Alias for 'MissionPlanner.MainV2.MAV.cs'
    This class exposes the currentState of the vehicle. Using this, we will be able to access all variables under the 'Status' tab in mission planner.
    e.g. 'cs.battery_remaining' will return an integer from 0..100 that represents the battery level of the vehicle.

    3. Script / mavutil
    Alias for 'this'
    This class is run by Mission Planner that exposes all the other classes. It also provides some useful functions such as timing or getting params.
    e.g. Script.Sleep() or mavutil.Sleep() will cause the script to delay its execution.

All exposed classes:
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: MAV
    Alias: MainV2.comPort
    Source Code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/ExtLibs/Utilities/IMAVLinkInterface.cs
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: cs
    Alias: MainV2.comPort.MAV.cs
    Source Code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/Script.cs
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: Script / mavutil
    Alias: this
    Source Code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/Script.cs
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: MainV2
    Alias: MainV2.instance
    Source Code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/MainV2.cs
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: FlightPlanner 
    Alias: FlightPlanner.instance
    Source Code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/GCSViews/FlightPlanner.cs
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: FlightData
    Alias: FlightData.instance
    Source Code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/GCSViews/FlightData.cs
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: Ports
    Alias: MainV2.Comports
    Source Code: N/A
    -----------------------------------------------------------------------------------------------------------------------------------
    Class: Joystick
    Alias: MainV2.joystick
    Source Code: N/A
    -----------------------------------------------------------------------------------------------------------------------------------

For more information, please refer to Using Python Scripts in Mission Planner:
https://ardupilot.org/planner/docs/using-python-scripts-in-mission-planner.html
"""

print("[INFO] Importing Dependencies...")

# Importing Python dependencies
# import sys
# sys.path.append(r"c:/python27/lib")
import socket
import json
import clr
import threading
import gc
import time
import datetime
import traceback

# Importing MissionPlanner dependencies
clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")
from MissionPlanner.Utilities import Locationwp, WaypointFile
# clr.AddReference("MAVLink")
import MAVLink
from MAVLink import mavlink_command_int_t
# Importing C# List primitive dependency 
clr.AddReference('System')
from System.Collections.Generic import List
from System import Func
print("[INFO] Starting Script...")


class MissionManager:
    """The Mission Manager Class interfaces with Mission Planner/MAVLink to dynamically change waypoints during a mission.
    """
    def __init__(self, connect=True, chunk_size=1024, port=7766):
        """Constructor

        Args:
            connect (bool, optional): decides if the connection to the backend server is opened on startup. Defaults to True
            chunk_size (int, optional): Defines the packet size of each TCP packet. Defaults to 1024
            port (int, optional): The ephemeral port number that the connection to the backend server will run on. 
        """
        # Attributes for Waypoint access from Mission Planner.
        self.id = int(MAVLink.MAV_CMD.WAYPOINT)  # id_mav_cmd for waypoints
        self.waypoint_count = 0  # The number of waypoints
        self.waypoints = []  # list of the waypoints
        self.live_data_rate = 1000 # Data send rate from drone to backend (in ms)
        self.cs_drone = MAV.MAV.cs # current state of drone object
        self.drone_connected = False
        # Attributes for Socket connection.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # The Python Socket class.
        # self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow socket to be reused.
        self.connection = None  # The Socket Connection that was received
        self.addr = None  # The Address of the received Socket Connection
        self.PORT = port  # The port number that the application is running on (default 7766)
        self.chunk_size = chunk_size  # The chunk size of the data sent a received (default 1024)
        self.messagesCount = 0 # The number of messages that have already been sent to the backend.
        # Attributes for Receive thread
        self.command_queue = [] # A queue of commands that were received
        self.command_queue_mutex = threading.Lock() # Mutex for command_queue
        self.quit = False # Allows for threads to terminate correctly

        # Lifeline Data params
        self.lifeline_mutex = threading.Lock() # Mutex to only allow 1 thread to read and write to the following params
        self.lifeline_status = 200 # initialise as IDLE state
        self.lifeline_distance = 0 # distance (m) of payload to albastross
        self.lifeline_velocity = 0 # velocity (m/s) from payload to albatross of the payload (+ moving down / - moving up)

        # Vision Data params
        self.vision_mutex = threading.Lock() # Mutex to only allow 1 thread to read and write to the following params
        self.vision_geotag_gps = {'x': 0, 'y': 0, 'z': 0}
        self.vision_geotag_box = {'x': 0, 'y': 0, 'z': 0}

        self.subscribe_to_mavlink_msg()
        # Start connection to backend
        if connect:
            self.__establish_connection()  # open the connection
        print("[TERMINATION] Communication Script has successfully Terminated.")


    def __str__(self):
        """Custom print str. Called by using 'print(MissionManager())' 

        Returns:
            string: A string that contains the lat, lng and alt of all waypoints.
        """
        if self.waypoint_count == 0:
            return "Waypoints ---> Empty"
        
        txt = "----------------------------------------------\nWaypoints\n [num]. latitude, longitude, altitude\n"
        for i in range(self.waypoint_count):
            wp = self.waypoints[i]
            txt += f"[ {i} ]. {wp.lat}, {wp.lng}, {wp.alt}\n"
        return txt + "----------------------------------------------"
    

    def __getitem__(self, index):
        """Custom get item. Is called by using 'wp = MissionManager()[index]'.

        Args:
            index (int): The index to get the waypoint at.

        Returns:
            Locationwp: The waypoint at the specified index, or None if it does not exist.
        """
        return self.waypoints[index] if index < self.waypoint_count else None
    

    def __setitem__(self, index, waypoint):
        """ Custom set item. Is called by using 'MissionManager()[index] = waypoint'.

        Args:
            index (int): The index to set the waypoint at.
            waypoint (Locationwp): The waypoint to be set.
        """
        if index < self.waypoint_count:
            self.waypoints[index] = waypoint
        else:
            print("[ERROR] Setting Waypoint at index " + str(index) + " was out of bounds.")
    

    def sync(self):
        """Syncs all the waypoints in Mission Planner to waypoints list (overrides any previous changes if update was not called)
        """
        try:
            print("[INFO] Syncing Live Waypoints...")
            self.waypoint_count = MAV.getWPCount()
            self.waypoints = [MAV.getWP(index) for index in range(MAV.getWPCount())]
            self.cs_drone = cs  # update current state of drone object
            self.drone_connected = True
            print("[INFO] Syncing Live Waypoints Successful")
        except:
            self.drone_connected = False
            print("[INFO] Syncing Live Waypoints Failed! The vehicle may not be connected, trying again in 10 seconds...")


    def append(self, waypoint):
        """Adds a waypoint to the end of the mission/list

        Args:
            waypoint (Locationwp): The waypoint to be appended into the list.
        """
        # Update waypoint count
        self.waypoint_count += 1
        # Append to class list and Mission planner
        self.waypoints.append(waypoint)


    def insert(self, index, waypoint):
        """Inserts a waypoint at a certain index.

        Args:
            index (int): The index to insert the waypoint at.
            waypoint (Locationwp): The waypoint to be inserted into the list.
        """
        # Update waypoint count
        self.waypoint_count += 1
        # Insert into class list and Mission Planner
        self.waypoints.insert(index, waypoint)


    def remove(self, index):
        """Removes a waypoint at a certain index.

        Args:
            index (int): The index to remove the waypoint at.
        """
        self.waypoints.remove(index)


    def swap(self, index1, index2):
        """Swaps waypoints at two indices.

        Args:
            index1 (_type_): The first waypoint to swap with.
            index2 (_type_): The second waypoint to swap with.
        """
        self.waypoints[index1], self.waypoints[index2] = self.waypoints[index2], self.waypoints[index1]


    def update(self):
        """Updates Mission Planner on the modified waypoints
        """
        self.waypoints.insert(0, self.create_wp(**{'lat': self.cs_drone.lat, 'long': self.cs_drone.lng, 'alt': self.cs_drone.alt}))
        # print("HELP", self.cs_drone.lat, self.cs_drone.lng, self.cs_drone.alt)
        # print(self.waypoints[0])
        MAV.setWPTotal(len(self.waypoints))
        
        for i in range(len(self.waypoints)):
            MAV.setWP(self.waypoints[i], i, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

        MAV.setWPACK()  # Send waypoint ACK
        print("[UPLOAD] AUTO MISSION SUCCESSFULLY UPLOADED")
        # self.__set_home(self.waypoints[0])  # Set the home waypoint as the first waypoint
        # self.__set_home(self.create_wp(self.cs_drone.lat, self.cs_drone.lng, self.cs_drone.alt))  # Set the home waypoint as the vehicle's current location
        
    

    def create_wp(self, **kwargs):
        """Creates a waypoint

        Args (provided inside the kwargs dict):
            lat (float): The latitude in degrees.
            lng (float): longitude in degrees.
            alt (float): The altitude in meters.
            id  (int):   The waypoint id

        Returns:
            Locationwp: The Locationwp object which contains the lat, lng and alt. This is an object from of MAVLink/Mission Planner.
        """
        id = kwargs["id"] if "id" in kwargs.keys() else self.id
        try:
            wp = Locationwp().Set(kwargs['lat'], kwargs['lng'], kwargs['alt'], id)
        except Exception as e:
            if not ("lat" in kwargs.keys() and "long" in kwargs.keys() and "alt" in kwargs.keys()):
                print("[ERROR] lat, long, alt not passed properly")
            else:
                traceback.print_exc()
                print('[ERROR] Error creating waypoints')

        if "p1" in kwargs.keys():
            Locationwp.p1.SetValue(wp, kwargs["p1"])
        if "p2" in kwargs.keys():
            Locationwp.p2.SetValue(wp, kwargs["p2"])
        if "p3" in kwargs.keys():
            Locationwp.p3.SetValue(wp, kwargs["p3"])
        if "p4" in kwargs.keys():
            Locationwp.p4.SetValue(wp, kwargs["p4"])
        return wp
    

    def set_waypoint(self, lat, lng, alt, index):
        """Alters latitude, longitude and altitude of a waypoint via index and sets it into Mission Planner

        Args:
            lat (float): The latitude to be set in degrees.
            lng (float): longitude to be set in degrees.
            alt (float): The altitude to be set in meters.
            index (int): The index of the waypoint that will have its values changed.
        """
        wp = self[index]
        Locationwp.lat.SetValue(wp, lat)
        Locationwp.lng.SetValue(wp, lng)
        Locationwp.alt.SetValue(wp, alt)
        self[index] = wp

    
    def set_lat(self, index, value):
        """Alters latitude of a waypoint via index and sets it into Mission Planner.

        Args:
            index (int): The index of the waypoint to set the latitude.
            value (float): The latitude to be set in degrees.
        """
        wp = self[index]
        Locationwp.lat.SetValue(wp, value)
        self[index] = wp


    def set_lng(self, index, value):
        """Alters longitude of a waypoint via index and sets it into Mission Planner.

        Args:
            index (int): The index of the waypoint to set the longitude.
            value (float): The longitude to be set in degrees.
        """
        wp = self[index]
        Locationwp.lng.SetValue(wp, value)
        self[index] = wp


    def set_alt(self, index, value):
        """Alters altitude of a waypoint via index and sets it into Mission Planner.

        Args:
            index (int): The index of the waypoint to set the altitude.
            value (float): The altitude to be set in meters.
        """
        wp = self[index]
        Locationwp.alt.SetValue(wp, value)
        self[index] = wp
    

    def target_waypoint(self, index):
        """Sets the waypoint to go to in guided mode.
        Args:
            index (int): The index of the waypoint to set as target.
        """
        MAV.setGuidedModeWP(self.waypoints[index])


    def __set_home(self, waypoint):
        """Sets the home waypoint (NOTE: THIS SHOULD BE INDEX=0 IN THE WAYPOINTS LIST).
        This is a private function.

        Args:
            waypoint (Locationwp): The waypoint to be set as the home.
        """
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME, 0, 0, 0, 0, waypoint.lat, waypoint.lng, waypoint.alt)
        self.waypoints[0] = waypoint
    

    def toggle_arm_aircraft(self):
        # MAV.doCommand(MAVLink.MAV_CMD.RUN_PREARM_CHECKS, 0, 0, 0, 0, 0, 0, 0, False)
        # MAV.doCommand(MAVLink.MAV_CMD.COMPONENT_ARM_DISARM, 1, 0, 0, 0, 0, 0, 0, 0)
        # Attempt to Restart Mission (incase there was a previous mission that was not completed)
        try:
            if self.waypoint_count > 0:
                MAV.setWPCurrent(MAV.sysid, MAV.compid, 0) 
        except:
            pass
        MAV.setMode("QLOITER")
        if self.cs_drone and self.cs_drone.armed:
            MAV.doARM(False, True)
            print("[INFO] Toggled Drone to DISARMED")
            # MAV.doCommand(MAVLink.MAV_CMD.DO_SET_MODE, 208, 0, 0, 0, 0, 0, 0, 0)
            # MAV.doCommand(MAVLink.MAV_CMD.COMPONENT_ARM_DISARM, 1, 0, 0, 0, 0, 0, 0, 0)
        else: 
            # MAV.doCommand(MAVLink.MAV_CMD.COMPONENT_ARM_DISARM, 0, 21196, 0, 0, 0, 0, 0, 0)
            MAV.doARM(True, True)
            Script.Sleep(4000)
            print("[INFO] Toggled Drone to ARMED")
        MAV.setMode("AUTO")

    def __establish_connection(self):
        """Creates an open socket connection for the backend to connect to.
        This function is private.
        """
        HOST = ""  # Open to all IP addresses. Can set to be a specific one.
        try:
            print("[INFO] Waiting for a backend connection...")
            self.s.bind((HOST, self.PORT))
            self.s.listen(1)  # Listens for 1 connection
            self.connection, self.addr = self.s.accept()
            print("[INFO] Connected by " + str(self.addr))

            # start receive thread
            receive_thread = threading.Thread(target=self.__receive, name="receive_thread")
            send_live_data_thread = threading.Thread(target=self.send_live_data, name="send_live_data_thread")
            receive_thread.start()
            send_live_data_thread.start()

            # Sync vehicle until successful
            self.sync()
            last_time = time.time() # Keep track on how often we should attempt to sync to a vehicle

            # Handle commands received
            while not self.quit:
                # Attempt to sync to the vehicle every 5 seconds if no connection
                if not self.drone_connected and time.time() - last_time > 10:
                    last_time = time.time()
                    self.sync()
                # If there is a command, handle it
                if len(self.command_queue) > 0:
                    self.command_queue_mutex.acquire()
                    data = self.command_queue.pop(0)
                    self.command_queue_mutex.release()
                    # if data given is exit command
                    if data == "quit":
                        print("[TERMINATION] QUIT COMMAND WAS RECEIVED")
                        break  
                    self.handle_command(data)
            self.quit = True # stop the receive thread
            receive_thread.join()
            send_live_data_thread.join()
        except Exception as e:
            # print out error.
            print(traceback.format_exc())
            print("[ERROR] Error in Establish Connection")
        self.close()


    def __receive(self):
        """Performs the receiving of the data from the backend.
        """
        self.s.setblocking(0)
        while not self.quit:
            try:
                data = ""
                chunk_data = ""
                # Receive until end of text sent
                while not self.quit:
                    chunk_data = self.connection.recv(self.chunk_size).decode()  # receive data in 1024 bit chunks
                    m = len(chunk_data)
                    # print('end: ' + chunk_data[m-2:m])
                    data += chunk_data
                    if chunk_data[m-2:m] == '\n\n':
                        data = data.strip()
                        break
                    # print('[SOCKET STREAM]' + data)
                # Check if data exists (polling due to non-blocking)
                if data:
                    if data == 'quit': 
                        break
                    decoded_data = json.loads(data)
                    # Lock queue and insert new command
                    print('[INFO] Received Command: ' + decoded_data['command'])
                    self.command_queue_mutex.acquire()
                    self.command_queue.append(decoded_data)
                    self.command_queue_mutex.release()
                    # print('[INFO] command_queue', self.command_queue)
            except Exception as e:
                # print out error.
                print(traceback.format_exc())
        self.quit = True
        print("[TERMINATION] receive_thread has successfully terminated.")

    def handle_command(self, decoded_data):
        """This function handles any commands sent from the backend server.

        Args:
            data (bytes): The byte stream from the socket connection that is the data of the command.
        """
        command = decoded_data["command"]
        
        # Used in place of a switch-case as IronPython does not implement it.
        # NOTE: THIS SHOULD BE CHANGED TO AN ATTRIBUTE (ie. self.command_dict) ONCE ALL COMMANDS ARE DONE.
        command_dict = {Commands.OVERRIDE: Commands.override, 
                        Commands.OVERRIDE_FLIGHTPLANNER: Commands.override_flightplanner,
                        Commands.SYNC_SCRIPT: Commands.sync_script,
                        Commands.TOGGLE_ARM: Commands.toggle_arm_aircraft,
                        Commands.GET_FLIGHTPLANNER_WAYPOINTS: Commands.get_flightplanner_waypoints,
                        Commands.SEND_COMMAND_INT: Commands.send_command_int,
                        Commands.TOGGLE_WEATHER_VANING: Commands.toggle_weather_vaning,
                        Commands.CHANGE_DRONE_MODE: Commands.change_drone_mode,
                        }  
        
        # run the command
        try:
            command_dict[command](Commands(), self, decoded_data)
        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Unknown Command Was Given.")


    def close(self):
        """Safely closes the Socket Connection.
        """
        try:
            self.quit = True
            self.connection.close()
            self.s.close()
        except Exception as e:
            print(traceback.format_exc())
        
        print("[TERMINATION] Connection to " + str(self.addr) + " was lost.")
    

    def convert_to_locationwp(self, waypoints):
        """Converts a list of dictionaries to the waypoints that mission planner uses.

        Args:
            waypoints (list[dict]): A list of dictionaries containing waypoints.

        Returns:
            list[Locationwp]: The list of Locationwp for Mission Planner to use.
        """
        n = len(waypoints)  # number of waypoints
        res = [None for _ in range(n)]  # initialize list

        for i in range(n):
            res[i] = self.create_wp(**waypoints[i])
        return res
    
    def send_live_data(self):
        """Sends live data from the drone to the backend. Is run as a thread and sends data every 'live_data_rate' ms.
        """
        Script.Sleep(self.live_data_rate)
        while not self.quit:
            if self.cs_drone:
                try:
                    messages_to_send = []
                    for message in self.cs_drone.messages[self.messagesCount:]:
                        messages_to_send.append({'time': str(message[0]), 'message': message[1]})
                        self.messagesCount += 1
                    self.lifeline_mutex.acquire()
                    self.vision_mutex.acquire()
                    data = json.dumps({
                        "command":Commands.LIVE_DRONE_DATA,
                        "data":{
                            "timestamp": datetime.datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
                            "lat": float(self.cs_drone.lat),
                            "lng": float(self.cs_drone.lng),
                            "alt": float(self.cs_drone.alt),
                            "distTraveled": float(self.cs_drone.distTraveled),
                            "DistToHome": float(self.cs_drone.DistToHome),
                            "airspeed": float(self.cs_drone.airspeed),
                            "groundspeed": float(self.cs_drone.groundspeed),
                            "verticalspeed": float(self.cs_drone.verticalspeed),
                            "battery_voltage": float(self.cs_drone.battery_voltage),
                            "battery_remaining": float(self.cs_drone.battery_remaining),
                            "propulsion_battery":float(self.cs_drone.battery_cell1),
                            "avionics_battery":float(self.cs_drone.battery_voltage2),
                            "armed": self.cs_drone.armed,
                            "drone_connected": self.drone_connected,
                            "weather_vaning": bool(Script.GetParam("Q_WVANE_ENABLE")),
                            "sonarrange": float(self.cs_drone.sonarrange),
                            "messages": messages_to_send,
                            "lifeline_status": self.lifeline_status,
                            "lifeline_distance": self.lifeline_distance,
                            "lifeline_velocity": self.lifeline_velocity,
                            "vision_geotag_gps": self.vision_geotag_gps,
                            "vision_geotag_box": self.vision_geotag_box
                            },
                        })
                    self.vision_mutex.release()
                    self.lifeline_mutex.release()
                    # print('[MESSAGES TO SEND]', messages_to_send)
                    self.connection.sendall((data + '\n\n').encode())
                    Script.Sleep(self.live_data_rate)
                except Exception as e:
                    print(traceback.format_exc())
        print("[TERMINATION] send_live_data_thread has successfully terminated")


    def set_cube_relay_pin(self, pin_num, pin_state):
        """Sets a chosen relay pin on the cube to either high (0V) or low (5V)
        """

        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_RELAY, pin_num, pin_state)
        pin_bool ='LOW' if pin_state == 0 else 'HIGH'
        print(" [INFO] Set Relay Pin " + pin_num + " to " + pin_bool)

    def send_command_int(self, target_system, target_component, command_code, kwargs):
        """Sends a custom command that is defined by the team and each project section.
        Also have a look at mav_enums.py in the 'MAVLink_Pipeline' Repository (Is a git submodule in Mission Management).
        For more information refer to: https://mavlink.io/en/messages/common.html#COMMAND_INT
        Args:
            target_system (int): System ID
            target_component (int): Component ID
            command_code (int): The scheduled action for the mission item.
            kwargs (dict): {
                frame (int, optional): The coordinate system of the COMMAND. Defaults to 0.
                current (int, optional): Not used. Defaults to 0.
                autocontinue (int, optional): Not used (set 0). Defaults to 0.
                param1 (float, optional): A free parameter that can be used depending on the command. Defaults to 0.
                param2 (float, optional):  A free parameter that can be used depending on the command. Defaults to 0.
                param3 (float, optional):  A free parameter that can be used depending on the command. Defaults to 0.
                param4 (float, optional):  A free parameter that can be used depending on the command. Defaults to 0.
                x (int, optional): PARAM5 / local: x position in meters * 1e4, global: latitude in degrees * 10^7. Defaults to 0.
                y (int, optional): PARAM6 / local: y position in meters * 1e4, global: longitude in degrees * 10^7. Defaults to 0.
                z (float, optional): PARAM7 / z position: global: altitude in meters (relative or absolute, depending on frame). Defaults to 0.
            }
        """
        try:
            keys = kwargs.keys()
            frame = kwargs["frame"] if "frame" in keys else 0
            current = kwargs["current"] if "current" in keys else 0
            autocontinue = kwargs["autocontinue"] if "autocontinue" in keys else 0
            param1 = kwargs["param1"] if "param1" in keys else 0
            param2 = kwargs["param2"] if "param2" in keys else 0
            param3 = kwargs["param3"] if "param3" in keys else 0
            param4 = kwargs["param4"] if "param4" in keys else 0
            x = kwargs["x"] if "x" in keys else 0
            y = kwargs["y"] if "y" in keys else 0
            z = kwargs["z"] if "z" in keys else 0
            # print('WUT', MAVLink.MAV_CMD.WAYPOINT)
            commandIntPacket = mavlink_command_int_t()
            mavlink_command_int_t.target_system.SetValue(commandIntPacket, target_system)
            mavlink_command_int_t.target_component.SetValue(commandIntPacket, target_component)
            mavlink_command_int_t.command.SetValue(commandIntPacket, command_code)
            mavlink_command_int_t.frame.SetValue(commandIntPacket, frame)
            mavlink_command_int_t.current.SetValue(commandIntPacket, current)
            mavlink_command_int_t.autocontinue.SetValue(commandIntPacket, autocontinue)
            mavlink_command_int_t.param1.SetValue(commandIntPacket, param1)
            mavlink_command_int_t.param2.SetValue(commandIntPacket, param2)
            mavlink_command_int_t.param3.SetValue(commandIntPacket, param3)
            mavlink_command_int_t.param4.SetValue(commandIntPacket, param4)
            mavlink_command_int_t.x.SetValue(commandIntPacket, x)
            mavlink_command_int_t.y.SetValue(commandIntPacket, y)
            mavlink_command_int_t.z.SetValue(commandIntPacket, z)
            # command , target sysid, target compid   used to keep track of the remote state
            MAV.sendPacket(commandIntPacket, target_system, target_component)

            # Cannot do this as command_code must be a c# MAV_CMD enum
            # return MAV.doCommandInt(target_system, target_component, command_code, current, autocontinue, param1, param2, param3, param4, x, y, z)
            print("[INFO] Sending COMMAND INT Successful")
        except Exception as e:
            print(traceback.format_exc())
            print("[ERROR] Failed to send COMMAND INT")
    
    
    def toggle_weather_vaning(self):
        """Toggles on and off weather vaning on the plane (Weather Vaning makes the drone face with the wind).
        """
        try:
            status = bool(Script.GetParam("Q_WVANE_ENABLE"))
            Script.ChangeParam("Q_WVANE_ENABLE", not status)
            print("[INFO] Set Weather Vaning to: " + str(not status))
        except Exception as e:
            print(traceback.format_exc())
            print("[ERROR] Failed to toggle WEATHER VANING, Current State: " + str(status))
    
    def change_drone_mode(self, mode):
        """Sets the plane's mode. Please refer to MAVLINK Flight modes:
        https://ardupilot.org/plane/docs/flight-modes.html#flight-modes
        i.e. "QLOITER", "LOITER", "QRTL", "RTL", "MANUAL", "GUIDED", "AUTO", 
        All modes can also be found on Mission Planner under Data -> Actions -> Dropdown for Set Mode
        """
        try:
            MAV.setMode(mode)
            print("[INFO] Set plane's mode to: " + mode)
        except Exception as e:
            print(traceback.format_exc())
            print("[ERROR] Failed to change plane's mode to RTL")
        

    def NamedValueFloatHandler(self, message):
        """Function handler for when a NAMED_VALUE_FLOAT message is received over mavlink
        https://mavlink.io/en/messages/common.html#NAMED_VALUE_FLOAT

        Args:
            message (_type_): The message packet from c#.

        Returns:
            boolean: True if the message was handled successfully
        """
        if int(message.msgid) == MAVLink.MAVLINK_MSG_ID.NAMED_VALUE_FLOAT.value__:
            print("NAMED_VALUE_FLOAT from MAV.SubscribeToPacketType with sysid: " + str(message.sysid) + ", compid: " + str(message.compid))
            # If message from LIFELINE
            if int(message.sysid) == 1 and int(message.compid) == 171:
                # print(dir(message.data))
                name = str(bytearray(message.data.name)).rstrip('\x00') # convert byte array to string and remove null characters
                value = message.data.value
                self.lifeline_mutex.acquire()
                if name == "LFL_STATUS":
                    print(name, value)
                    self.lifeline_status = int(value)
                elif name == "LFL_DIST":
                    self.lifeline_distance = float(value)
                elif name == "LFL_VEL":
                    self.lifeline_velocity = float(value)
                self.lifeline_mutex.release()
                
        return True

    def DebugVectHandler(self,message):
        if int(message.msgid) == MAVLink.MAVLINK_MSG_ID.DEBUG_VECT.value__:
            print("DEBUG_VECT from MAV.SubscribeToPacketType with sysid: " + str(message.sysid) + ", compid: " + str(message.compid))
            # If message from VISION
            if int(message.sysid) == 1 and int(message.compid) == 170:
                name = str(bytearray(message.data.name)).rstrip('\x00')
                x = float(message.data.x)
                y = float(message.data.y)
                z = float(message.data.z)
                self.vision_mutex.acquire()
                if name == "GEOTAG_GPS":
                    self.vision_geotag_gps = {'x': x, 'y': y, 'z': z}
                elif name == "GEOTAG_BOX":
                    self.vision_geotag_box = {'x': x, 'y': y, 'z': z}
                self.vision_mutex.release()
                

    def subscribe_to_mavlink_msg(self):
        """Function to subscribe to MAVLink messages """
        # subscribe to NAMED_VALUE_FLOAT for Lifeline - Lifeline send status updates in this form
        sub_named_value_float = MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.NAMED_VALUE_FLOAT, Func[MAVLink.MAVLinkMessage, bool] (self.NamedValueFloatHandler), 1, 171) # sysid=1, compid=169 (lifeline)
        # subscribe to DEBUG_VECT for Vision - Vision sends target geolocation and bounding box size/position info in this form
        sub_debug_vect = MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.DEBUG_VECT, Func[MAVLink.MAVLinkMessage, bool] (self.DebugVectHandler), 1, 170) # sysid=1, compid=170 (vision)

        #  unsubscriptions are usually handled when socket is closed, but can be manually done with the following code:
        #  MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.COMMAND_INT.value__, sub);
        #  MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.DEBUG_VECT.value__, sub);
        

class Commands:
    """An ENUM containing all the commands that the backend server can send for execution on mission planner.
    The functions in this class will execute the command.
    """
    OVERRIDE = "OVERRIDE"
    OVERRIDE_FLIGHTPLANNER = "OVERRIDE_FLIGHTPLANNER"
    SYNC_SCRIPT = "SYNC_SCRIPT"
    TOGGLE_ARM = "TOGGLE_ARM"
    GET_FLIGHTPLANNER_WAYPOINTS = "GET_FLIGHTPLANNER_WAYPOINTS"
    LIVE_DRONE_DATA = "LIVE_DRONE_DATA"
    SET_CUBE_RELAY_PIN = "SET_CUBE_RELAY_PIN"
    SEND_COMMAND_INT = "SEND_COMMAND_INT"
    TOGGLE_WEATHER_VANING = "TOGGLE_WEATHER_VANING"
    CHANGE_DRONE_MODE = "CHANGE_DRONE_MODE"


    def override(self, mission_manager, decoded_data):
        """Overrides all the waypoints in mission planner.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
            decoded_data (Dict): The data required to execute the command. Usually received from the backend.

        Returns:
            Action: An override action with the waypoints to override with.
        """
        
        try:
            if decoded_data["init_mode"] is not None: # set to guided, loiter or qloiter before overriding waypoints in flight
                MAV.setMode(decoded_data["init_mode"])
                print("[OVERRIDE] Drone mode Transitioning to " + decoded_data["init_mode"])
                Script.Sleep(4000)
            waypoints = decoded_data["waypoints"]
            recv_waypoints = mission_manager.convert_to_locationwp(waypoints)
            if decoded_data["vtol_transition_mode"] is not None:
                vtol_transition_wp = mission_manager.create_wp(**{'lat': 0, 'long': 0, 'alt': decoded_data["takeoff_alt"], 'id': int(MAVLink.MAV_CMD.DO_VTOL_TRANSITION)})
                Locationwp.p1.SetValue(vtol_transition_wp, decoded_data["vtol_transition_mode"]) # 3 for multicoptor, 4 fixed wing
                recv_waypoints.insert(0, vtol_transition_wp)
            if decoded_data["takeoff_alt"] is not None:
                recv_waypoints.insert(0, mission_manager.create_wp(**{'lat': 0, 'long': 0, 'alt': decoded_data["takeoff_alt"], 'id': int(MAVLink.MAV_CMD.VTOL_TAKEOFF)}))
            if decoded_data["do_RTL"]:
                recv_waypoints.append(mission_manager.create_wp(**{'lat': 0, 'long': 0, 'alt': 0, 'id': int(MAVLink.MAV_CMD.RETURN_TO_LAUNCH)}))
            mission_manager.waypoints = recv_waypoints
            mission_manager.waypoint_count = len(recv_waypoints)
            mission_manager.update()
            # Attempt to Restart Mission (incase there was a previous mission that was not completed)
            try:
                if mission_manager.waypoint_count > 0:
                    MAV.setWPCurrent(MAV.sysid, MAV.compid, 0) 
            except:
                pass
            if decoded_data["end_mode"] is not None: # Set mode back to AUTO
                Script.Sleep(8000)
                print("[OVERRIDE] Drone mode Transitioning to " + decoded_data["end_mode"])
                MAV.setMode(decoded_data["end_mode"])
            print("[COMMAND] OVERRIDE Waypoint Command Executed.")
        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Handling OVERRIDE COMMAND: Waypoints sent from backend does not exist or a Live Drone is not connected.")


    def override_flightplanner(self, mission_manager, decoded_data):
        """Overrides all the waypoints in the flight planner GUI.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
            decoded_data (Dict): The data required to execute the command. Usually received from the backend.

        Returns:
            Action: An override_flightplanner action with the waypoints to override with.
        """
        try:
            print(decoded_data)
            waypoints = decoded_data["waypoints"]
            recv_waypoints = mission_manager.convert_to_locationwp(waypoints)
            # home = mission_manager.waypoints[0]
            # recv_waypoints.insert(0, home)
            # print("[override_flightplanner] takeoff_alt: ", decoded_data["takeoff_alt"], decoded_data["vtol_transition_mode"])
            if decoded_data["vtol_transition_mode"] is not None:
                vtol_transition_wp = mission_manager.create_wp(**{'lat': 0, 'long': 0, 'alt': decoded_data["takeoff_alt"], 'id': int(MAVLink.MAV_CMD.DO_VTOL_TRANSITION)})
                Locationwp.p1.SetValue(vtol_transition_wp, decoded_data["vtol_transition_mode"]) # 3 for multicoptor, 4 fixed wing
                recv_waypoints.insert(1, vtol_transition_wp)
            if decoded_data["takeoff_alt"] is not None:
                recv_waypoints.insert(1,mission_manager.create_wp(**{'lat': 0, 'long': 0, 'alt': decoded_data["takeoff_alt"], 'id': int(MAVLink.MAV_CMD.VTOL_TAKEOFF)}))
            if decoded_data["do_RTL"]:
                recv_waypoints.append(mission_manager.create_wp(**{'lat': 0, 'long': 0, 'alt': decoded_data["takeoff_alt"], 'id': int(MAVLink.MAV_CMD.RETURN_TO_LAUNCH)}))
            FlightPlanner.WPtoScreen(List[Locationwp](recv_waypoints))
            print("[COMMAND] OVERRIDE_FLIGHTPLANNER Waypoints Command Executed.")
        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Handling OVERRIDE_FLIGHTPLANNER COMMAND.")


    def sync_script(self, mission_manager, decoded_data):
        """Syncs the communication script locationwp with the self.waypoints in this class.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
            decoded_data (Dict): The data required to execute the command. Usually received from the backend.

        Returns:
            Action: An sync_script action.
        """
        try:
            mission_manager.sync()
            print("[COMMAND] SYNC SCRIPT Command Executed.")
        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Handling SYNC_SCRIPT COMMAND.")


    def toggle_arm_aircraft(self, misson_manager, decoded_data):
        try:
            misson_manager.toggle_arm_aircraft()
            print("[COMMAND] ARM Command Executed.")
        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Handling ARM COMMAND.")


    def get_flightplanner_waypoints(self, mission_manager, decoded_data):
        """Gets the waypoints from the Flightplanner tab and sends it to the backend.

        Args:
            mission_manager MissionManager: The mission manager class connected to the mission planner.
            decoded_data (Dict): The data required to execute the command. Usually received from the backend.
        """
        try:
            # print(type(mission_manager.FlightPlanner))
            # res = mission_manager.FlightPlanner.GetCommandList()
            n = mission_manager.FlightPlanner.Commands.Rows.Count
            res = {"command": Commands.GET_FLIGHTPLANNER_WAYPOINTS, "waypoints":[]}
            for i in range(n):
                res["waypoints"].append({
                    "id": int(FlightPlanner.getCmdID(FlightPlanner.Commands.Rows[i].Cells[0].Value)), # Command as a string
                    "lat": float(FlightPlanner.Commands.Rows[i].Cells[5].Value), # Lat
                    "long": float(FlightPlanner.Commands.Rows[i].Cells[6].Value), # Lng
                    "alt": float(FlightPlanner.Commands.Rows[i].Cells[7].Value), # Alt
                })
            # print('Command List', res)
            mission_manager.connection.sendall((json.dumps(res) + '\n\n').encode())
            print("[COMMAND] GET_FLIGHTPLANNER_WAYPOINTS Command Executed.")
        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Handling GET_FLIGHTPLANNER_WAYPOINTS COMMAND.")

    
    def set_cube_relay_pin(self, mission_manager, decoded_data):
        """Sets a chosen relay pin on the cube either high or low
        
        Args:
            mission_manager MissionManager: The mission manager class connected to the mission planner.
            decoded_data (Dict): The data required to execute the command. Usually received from the backend
        """

        try:
            pin_num = decoded_data["pin_num"]
            pin_state = decoded_data["pin_state"]
            mission_manager.set_cube_relay_pin(pin_num, pin_state)
            print("[COMMAND] MAV_CMD_DO_SET_RELAY Command Executed.")

        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Handling MAV_CMD_DO_SET_RELAY COMMAND.")

    def send_command_int(self, mission_manager, decoded_data):
        """Sends a COMMAND_INT message to Mission Planner
        
        Args:
            mission_manager MissionManager: The mission manager class connected to the mission planner.
            decoded_data (Dict): The data required to execute the command. Usually received from the backend
        """

        try:
            target_system = decoded_data["target_system"]
            target_component = decoded_data["target_component"]
            command_code = decoded_data["command_code"]
            kwargs = decoded_data["kwargs"]

            kwargs = decoded_data["kwargs"]
            mission_manager.send_command_int(target_system, target_component, command_code, kwargs)

        except Exception as e:
            print(traceback.format_exc())
            print("[COMMAND] ERROR: Handling MAV_COMMAND_INT COMMAND")


    def toggle_weather_vaning(self, mission_manager, decoded_data):
        """Toggles on and off weather vaning on the plane (Weather Vaning makes the drone face with the wind).
        """
        try:
            mission_manager.toggle_weather_vaning()
        except Exception as e:
            print(traceback.format_exc())
            print("[ERROR] ERROR: Handling TOGGLE_WEATHER_VANING COMMAND")
    
    def change_drone_mode(self, mission_manager, decoded_data):
        """Sets the plane's mode. Please refer to MAVLINK Flight modes:
        https://ardupilot.org/plane/docs/flight-modes.html#flight-modes
        i.e. "QLOITER", "LOITER", "QRTL", "RTL", "MANUAL", "GUIDED", "AUTO", 
        All modes can also be found on Mission Planner under Data -> Actions -> Dropdown for Set Mode
        """
        try:
            mission_manager.change_drone_mode(decoded_data["mode"])
        except Exception as e:
            print(traceback.format_exc())
            print("[ERROR] Error handling CHANGE DRONE MODE COMMAND")
    

# ------------------------------------ End Classes ------------------------------------
# def waypoint_mavlink_test():
#     """Sets the current mission to hard-coded waypoints using MAVLink functions.
#     """
#     id = int(MAVLink.MAV_CMD.WAYPOINT) # id_mav_cmd for waypoints
#     MAV.doCommand
#     home = Locationwp().Set(-37.8238872, 145.0538635, 0, id)

#     takeoff = Locationwp()
#     Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.TAKEOFF))
#     Locationwp.p1.SetValue(takeoff, 15)
#     Locationwp.alt.SetValue(takeoff, 50)

#     wp1 = Locationwp().Set(-37.8408347, 145.2241516, 100, id)
#     wp2 = Locationwp().Set(-37.8411058, 145.2569389, 100, id)
#     wp3 = Locationwp().Set(-37.8657742, 145.2680969, 100, id)
#     wp4 = Locationwp().Set(-37.8818991, 145.2234650, 100, id)

#     MAV.setWPTotal(6)
#     MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
#     MAV.setWP(takeoff, 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
#     MAV.setWP(wp1, 2, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
#     MAV.setWP(wp2, 3, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
#     MAV.setWP(wp3, 4, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
#     MAV.setWP(wp4, 5, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
#     MAV.setWPACK()

#     # Set Home waypoint
#     MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME, 0, 0, 0, 0, -37.8238872, 145.0538635, 0)
    

# def waypoint_manager_test():
#     """Adds hard-coded waypoints to the current mission using the Mission Manager Class.
#     """
#     mm = MissionManager(sync=False)  # Sync is set to False so that we can overwrite existing waypoints

#     print("After Syncing")
#     print(mm)
#     home = mm.create_wp(-37.8238872, 145.0538635, 0)

#     takeoff = Locationwp()
#     Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.TAKEOFF))
#     Locationwp.p1.SetValue(takeoff, 15)
#     Locationwp.alt.SetValue(takeoff, 50)

#     wp1 = mm.create_wp(-37.8408347, 145.2241516, 100)
#     wp2 = mm.create_wp(-37.8411058, 145.2569389, 100)
#     wp3 = mm.create_wp(-37.8657742, 145.2680969, 100)
#     wp4 = mm.create_wp(-37.8818991, 145.2234650, 100)

#     mm.append(home)
#     mm.append(takeoff)
#     mm.append(wp1)
#     mm.append(wp2)
#     mm.append(wp3)
#     mm.append(wp4)
#     mm.update()
#     print("After Adding")
#     print(mm)

#     # Sleep for 5 seconds before editing waypoint 2
#     print("Sleeping for 5 seconds")
#     Script.Sleep(5000)
#     print("Changing waypoint 2")
#     mm.set_waypoint(-37.7202198, 145.1486206, 100, 2)
#     mm.update()

#     print("Set Guided Mode Waypoint to: wp3 (index 4)")
#     mm.target_waypoint(4)
    
#     # Sleep for 5 seconds before adding a new waypoint
#     print("Sleeping for 5 seconds")
#     Script.Sleep(5000)
#     print("Adding a waypoint")
#     wp5 = mm.create_wp(-37.9154926, 145.1170349, 100)
#     mm.append(wp5)
#     mm.update()

        
# NOTE: Script is run as a module and not as __main__.
#waypoint_mavlink_test()
#waypoint_manager_test()

def get_ip():
    """Gets the IPs of the current device and prints them.
    """
    hostname = socket.gethostname()
    addr = min(socket.gethostbyname_ex(hostname)[2])
    print("[INFO] Hostname: " + hostname + "\n[INFO] Address(es): " + str(addr))

get_ip()  # Print out the IPs of the device running Mission Planner.
mm = MissionManager(chunk_size=8192)  # Create a mission manager class.
del mm # garbage collect MissionManager to fully delete socket/port resources
gc.collect() # force manual garbage collect
print("[TERMINATION] Script Terminated!")

