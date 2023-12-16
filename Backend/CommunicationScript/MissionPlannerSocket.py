import socket
import threading
import json
import time
from mav_enums import *

class MissionPlannerSocket():
    """MissionPlannerSocket maintains the connection between the Backend Server and the Mission Planner device.
    This class is run on the Backend Server and requires the IP address of the device running Mission Planner (With the Communication Script running).
    The main purpose of this class is to handle sending and receiving data asynchronously on the Backend Server from the Mission Planner Device.
    """
    def __init__(self, port):
        """Constructor that sets up the Socket Connection.

        Args:
            host (str): The IP of the host to connect to.
            port (int): The port number of the application to connect to.
        """
        # self.HOST = host
        self.PORT = port
        self.HOST = "CONNECT TO MISSION PLANNER"
        self.COMMANDS = Commands()
        
        # Attributes for Receive thread
        self.command_queue = [] # A queue of commands that were received
        self.command_queue_mutex = threading.Lock() # Mutex for command_queue
        self.quit = False # Allows for threads to terminate correctly
        self.live_data_mutex = threading.Lock()
        self.live_data = {}
        self.s = None
        self.connected = False
        self.messages = [] # the list containing all messages from mission planner

    def initialise_dronelink(self, ip):
        if self.connected:
            print("[ERROR] A connection has already been made, please restart the server to reconnect.")
            return
        self.HOST = ip
        # Create Socket and connect to address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chunk_size = 8192
        try:
            self.connect()
            self.connected = True
            return True
        except Exception:
            print("[ERROR] Failed to initilise connection to dronelink.")
            self.HOST = "CONNECT TO MISSION PLANNER"
            return False


    def connect(self):
        """Connects the Socket to the host and port, if successful, a new thread will be created to handle sends and receives.
        """
        print("[INFO] Attempting to connect to (" + self.HOST + ":" + str(self.PORT) + ")")
        try:
            self.s.connect((self.HOST, self.PORT))
            # Create a new thread to handle the data received and execute the command.
            receive_thread = threading.Thread(target=self.__receive, name="receive_thread")
            handle_command_thread = threading.Thread(target=self.handle_command, name="handle_command_thread")
            receive_thread.start()
            handle_command_thread.start()
        except Exception as e:
            print("[ERROR] " + str(e))
            self.close()
    
    def __receive(self):
        """Performs the receiving of the data from mission planner.
        """
        self.s.setblocking(0)
        while not self.quit:
            try:
                data = ""
                chunk_data = ""
                # Receive until end of text sent
                while not self.quit:
                    chunk_data = self.s.recv(self.chunk_size)  # receive data in chunks
                    if chunk_data:
                        m = len(chunk_data)
                        data += chunk_data
                        # If the chunk is the end of a packet
                        if chunk_data[m-2:m] == '\n\n': # Packets are delimited by double newline '\n\n'
                            data = data.strip()
                            break
                    # print('[SOCKET STREAM]' + data)
                # Check if data exists (polling due to non-blocking)
                if data:
                    if data == 'quit': break
                    decoded_data = json.loads(data)
                    # Lock queue and insert new command
                    if decoded_data['command'] != self.COMMANDS.LIVE_DRONE_DATA:
                        print('\n[INFO] Received Command: ' + decoded_data['command'])
                    self.command_queue_mutex.acquire()
                    self.command_queue.append(decoded_data)
                    self.command_queue_mutex.release()
                    # print('[INFO] command_queue', self.command_queue)
            except Exception as e:
                continue
        self.quit = True
        print("\n[TERMINATION] receive_thread has successfully terminated.")


    def handle_command(self):
        """This function handles any commands sent from the mission planner script.

        Args:
            data (bytes): The byte stream from the socket connection that is the data of the command.
        """
        # Handle commands received
        while not self.quit:
            # If there is a command
            if len(self.command_queue) > 0:
                
                self.command_queue_mutex.acquire()
                decoded_data = self.command_queue.pop(0)
                self.command_queue_mutex.release()

                command = decoded_data["command"]
                # run the command
                try:
                    if command == self.COMMANDS.GET_FLIGHTPLANNER_WAYPOINTS:
                        print('\n[COMMAND] Received from get_flightplanner_waypoint: ' + str(decoded_data))
                    elif command == self.COMMANDS.LIVE_DRONE_DATA:
                        # print("[DATA] " + str(decoded_data["data"]))
                        try:
                            self.live_data_mutex.acquire()
                            data = decoded_data["data"]
                            messages = data['messages']
                            self.messages = self.messages + messages
                            data['messages'] = []
                            try:
                                ll_status_key = str(int(data["lifeline_status"]))
                                data["lifeline_status"] = LifelineState.LifeLineStateDict[ll_status_key]
                                # print(data["lifeline_status"])

                            except Exception as e:
                                print("[MESSAGE] Encountered the following error when attempting to read lifeline status: " + str(e))
                            self.live_data = data
                            self.live_data_mutex.release()
                        except Exception as e:
                            pass
                    else:
                        print("[ERROR] Unknown Command Was Given.")
                except Exception as e:
                    print("[ERROR] " + str(e))
                    print("[COMMAND] ERROR: Unknown Command Was Given.")
        self.quit = True
        print("[TERMINATION] handle_command_thread has successfully terminated.")
        

    def close(self):
        """Safely closes the Socket.
        """
        if self.s is not None:
            self.s.sendall(bytes("quit") + '\n\n')
            self.s.shutdown(1)
            self.s.close()  # close socket
            self.quit = True
            print("[INFO] Connection to (" + self.HOST + ":" + str(self.PORT) + ") was lost.")

        

    def override_waypoints(self, waypoints, takeoff_alt=None, vtol_transition_mode=None, do_RTL=False, init_mode=None, end_mode=None):
        """Sends a command to overwrite all the waypoints in mission planner.
        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        data = json.dumps({
                        "command":self.COMMANDS.OVERRIDE, 
                        "waypoints": waypoints,
                        "takeoff_alt":takeoff_alt, 
                        "vtol_transition_mode": vtol_transition_mode,
                        "do_RTL": do_RTL,
                        "init_mode": init_mode,
                        "end_mode": end_mode,
                        })
        self.s.sendall(data + '\n\n')
    
    
    def override_flightplanner_waypoints(self, waypoints, takeoff_alt=None, vtol_transition_mode=None, do_RTL=False):
        """Sends a command to overwrite all the waypoints in the flight planner GUI.
        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        data = json.dumps({
                        "command":self.COMMANDS.OVERRIDE_FLIGHTPLANNER, 
                        "waypoints": waypoints, 
                        "takeoff_alt":takeoff_alt, 
                        "vtol_transition_mode": vtol_transition_mode,
                        "do_RTL": do_RTL,
                        })
        self.s.sendall(data  + '\n\n')


    def sync_script(self):
        """Sends a command to sync all the waypoints live on the drone to the mission planner script.
        """
        data = json.dumps({"command":self.COMMANDS.SYNC_SCRIPT})
        self.s.sendall(data  + '\n\n')

    def toggle_arm_aircraft(self):
        """Sends a command to toggle the arming state of the drone
        """
        data = json.dumps({"command":self.COMMANDS.TOGGLE_ARM})
        self.s.sendall(data  + '\n\n')


    def get_flightplanner_waypoints(self):
        """Sends a command to get all the waypoints in the flight planner.
        """
        data = json.dumps({"command":self.COMMANDS.GET_FLIGHTPLANNER_WAYPOINTS})
        self.s.sendall(data  + '\n\n')

    def toggle_weather_vaning(self):
        """Sends a command to toggle weather vaning on the drone
        """
        data = json.dumps({"command": self.COMMANDS.TOGGLE_WEATHER_VANING})
        self.s.sendall(data  + '\n\n')

    def change_drone_mode(self, mode):
        """Sends a command to change the plane's mode to return to launch (RTL)
        """
        data = json.dumps({"command": self.COMMANDS.CHANGE_DRONE_MODE, "mode": mode})
        self.s.sendall(data  + '\n\n')
    

    def set_cube_relay_pin(self, pin_num, pin_state):
        """Sends a command to set the state of a chosen relay pin on the cube. 
        Args: 
            pin_num: the relay pin number on the cube
            pin_state: the state the the user wishes to set the pin to (0 for high, or 1 for low)
        """
        data = json.dumps({"command": self.COMMANDS.SET_CUBE_RELAY_PIN, "pin_num": pin_num, "pin_state": pin_state})
        self.s.sendall(data + '\n\n')

    def send_command_int(self, target_system, target_component, command_code, **kwargs):
        """Sends a custom command that is defined by the team and each project section.
        Also have a look at mav_enums.py in the 'MAVLink_Pipeline' Repository (Is a git submodule in Mission Management).
        For more information refer to: https://mavlink.io/en/messages/common.html#COMMAND_INT
        Args:
            target_system (int): System ID
            target_component (int): Component ID
            command_code (int): The scheduled action for the mission item.
            kwargs: {
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
        data = json.dumps({
            "command": self.COMMANDS.SEND_COMMAND_INT, 
            "target_system": target_system, 
            "target_component": target_component, 
            "command_code": command_code,  
            "kwargs": kwargs
            })
        self.s.sendall(data + '\n\n')
        

class Commands:
    """An ENUM containing all the commands that the backend server can send for execution on mission planner.
    The functions in this class will execute the command.
    """
    PATH_GENERATION_SEARCH_AREA = "PATH_GENERATION_SEARCH_AREA"
    PATH_GENERATION_POINT_TO_POINT = "PATH_GENERATION_POINT_TO_POINT"
    PATH_GENERATION_FLY_TO_CIRCLE_TARGET = "PATH_GENERATION_FLY_TO_CIRCLE_TARGET"
    PATH_GENERATION_FLY_TO_TARGET_PAYLOAD = "PATH_GENERATION_FLY_TO_TARGET_PAYLOAD"
    PLANE_PARAMETER_UPDATE = "PLANE_PARAMETER_UPDATE"
    OVERRIDE = "OVERRIDE"
    OVERRIDE_FLIGHTPLANNER = "OVERRIDE_FLIGHTPLANNER"
    DIRECT_WAYPOINTS = "DIRECT_WAYPOINTS"
    SYNC_SCRIPT = "SYNC_SCRIPT"
    TOGGLE_ARM = "TOGGLE_ARM"
    GET_FLIGHTPLANNER_WAYPOINTS = "GET_FLIGHTPLANNER_WAYPOINTS"
    LIVE_DRONE_DATA = "LIVE_DRONE_DATA"
    SET_CUBE_RELAY_PIN = "SET_CUBE_RELAY_PIN"
    SEND_COMMAND_INT = "SEND_COMMAND_INT" 
    TOGGLE_WEATHER_VANING = "TOGGLE_WEATHER_VANING"
    CHANGE_DRONE_MODE = "CHANGE_DRONE_MODE"
    PATIENT_LOCATION = "PATIENT_LOCATION"
    DROP_LOCATION = "DROP_LOCATION"

if __name__ == "__main__":
    host = raw_input("Enter IP to connect to: ")

    
    PORT = 7766  # port number of the connection.
    mp_socket = MissionPlannerSocket(PORT)
    mp_socket.initialise_dronelink(host)

    # TESTING
    test_waypoints = [{"lat":-37.8238872, "long":145.0538635, "alt":0},
                        {"lat":-37.8408347, "long":145.2241516, "alt":100},
                        {"lat":-37.8411058, "long":145.2569389, "alt":100},
                        {"lat":-37.8657742, "long":145.2680969, "alt":100},
                        {"lat":-37.8818991, "long":145.2234650, "alt":100}]
    
    option = ''
    while True:
        print("--------------------------------------------------------------------------------------")
        print("[Command Selection Menu]")
        print("These Commands will be sent and executed on the Mission Planner Communication Script!")
        print("--------------------------------------------------------------------------------------")
        print("[ 1 ]. OVERRIDE FLIGHTPLANNER WAYPOINTS (Hardcoded Waypoints)")
        print("[ 2 ]. SYNC SCRIPT")
        print("[ 3 ]. OVERRIDE WAYPOINTS on Live Drone (Hardcoded waypoints)")
        print("[ 4 ]. ARM/DISARM AIRCRAFT")
        print("[ 5 ]. GET FLIGHTPLANNER WAYPOINTS")
        print("[ q ]. Quit")
        print("--------------------------------------------------------------------------------------")

        option = raw_input("Select Command To Execute (Enter 'q' to Quit): ")
        if option == '1':
            mp_socket.override_flightplanner_waypoints(test_waypoints, 20, 3)
        elif option == '2':
            mp_socket.sync_script()
        elif option == '3':
            mp_socket.override_waypoints(test_waypoints, 20, 3)
        elif option == '4':
            mp_socket.toggle_arm_aircraft()
        elif option == '5':
            mp_socket.get_flightplanner_waypoints()
        elif option == 'q':
            break
        else:
            print("Invalid Option.")
    mp_socket.close()
