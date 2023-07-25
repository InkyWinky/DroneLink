import socket
import threading
import json
import time

class MissionPlannerSocket():
    """MissionPlannerSocket maintains the connection between the Backend Server and the Mission Planner device.
    This class is run on the Backend Server and requires the IP address of the device running Mission Planner (With the Communication Script running).
    The main purpose of this class is to handle sending and receiving data asynchronously on the Backend Server from the Mission Planner Device.
    """
    def __init__(self, host, port):
        """Constructor that sets up the Socket Connection.

        Args:
            host (str): The IP of the host to connect to.
            port (int): The port number of the application to connect to.
        """
        self.HOST = host
        self.PORT = port
        self.COMMANDS = Commands()
        
        # Attributes for Receive thread
        self.command_queue = [] # A queue of commands that were received
        self.command_queue_mutex = threading.Lock() # Mutex for command_queue
        self.quit = False # Allows for threads to terminate correctly

        # Create Socket and connect to address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chunk_size = 1024 
        self.connect()
    
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
                
            # mp_socket_thread.join()
        except Exception as e:
            print("[ERROR] " + str(e))
            self.close()
    
    def __receive(self):
        """Performs the receiving of the data from mission planner.
        """
        self.s.setblocking(0)
        while not self.quit:
            try:
                data = self.s.recv(self.chunk_size)  # receive data in 1024 bit chunks
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
                        pass
                    else:
                        print("[ERROR] Unknown Command Was Given.")
                except Exception as e:
                    print("[ERROR] " + str(e))
                    print("[COMMAND] ERROR: Unknown Command Was Given.")
        self.quit = True
        print("\n[TERMINATION] handle_command_thread has successfully terminated.")
        

    def close(self):
        """Safely closes the Socket.
        """
        self.s.sendall(bytes("quit"))
        self.s.shutdown(1)
        self.s.close()  # close socket
        self.quit = True
        print("[INFO] Connection to (" + self.HOST + ":" + str(self.PORT) + ") was lost.")
        

    def override_waypoints(self, waypoints):
        """Sends an Action to overwrite all the waypoints in mission planner.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        action = self.COMMANDS.override(waypoints)
        self.s.sendall(bytes(action.serialize()))
    
    
    def override_flightplanner_waypoints(self, waypoints):
        """Sends an Action to overwrite all the waypoints in the flight planner GUI.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        action = self.COMMANDS.override_flightplanner(waypoints)
        self.s.sendall(bytes(action.serialize()))


    def sync_script(self):
        """Sends an Action to sync all the waypoints in the flight planner to the mission planner script.
        """
        action = self.COMMANDS.sync_script()
        self.s.sendall(bytes(action.serialize()))

    def arm_aircraft(self):
        action = self.COMMANDS.arm_disarm_aircraft()
        self.s.sendall(bytes(action.serialize()))


    def get_flightplanner_waypoints(self):
        action = self.COMMANDS.get_flightplanner_waypoints()
        self.s.sendall(bytes(action.serialize()))

class Action:
    """The class that is sent from the backend connection to execute commands on the mission planner script.
    """
    def __init__(self, command, arm=None):
        self.command = command
        self.waypoints = None
        self.arm = arm
        
    

    def serialize(self):
        """Serializes the Action into a json string to be sent over the socket.

        Returns:
            str: The Action in string format. {"command":command, "waypoints":waypoints}
        """
        return json.dumps({"command":self.command, "waypoints":self.waypoints, "arm":self.arm})


    def deserialize(self, data):
        """Deserializes the json string back into an Action class.

        Args:
            data (str): The string of the json to be converted back into a list of dictionaries.
        """
        decoded = json.loads(data)
        decoded_action = Action(decoded["command"])
        decoded_action.waypoints = decoded["waypoints"]
        return decoded_action


class Commands:
    """An ENUM containing all the commands that the backend server can send for execution on mission planner.
    The functions in this class will return an Action class that will be sent over the socket connection.
    """
    OVERRIDE = "OVERRIDE"
    OVERRIDE_FLIGHTPLANNER = "OVERRIDE_FLIGHTPLANNER"
    SYNC_SCRIPT = "SYNC_SCRIPT"
    ARM = "ARM"
    armed = False
    GET_FLIGHTPLANNER_WAYPOINTS = "GET_FLIGHTPLANNER_WAYPOINTS"
    LIVE_DRONE_DATA = "LIVE_DRONE_DATA"

    def override(self, waypoints):
        """Creates an action that is to be sent to overrides all the waypoints in mission planner.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.

        Returns:
            Action: An override action with the waypoints to override with.
        """
        action = Action(Commands.OVERRIDE)
        action.waypoints = waypoints
        return action
    

    def override_flightplanner(self, waypoints):
        """Creates an action that is to be sent to overrides all the waypoints in the flight planner GUI.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.

        Returns:
            Action: An override_flightplanner action with the waypoints to override with.
        """
        action = Action(Commands.OVERRIDE_FLIGHTPLANNER)
        action.waypoints = waypoints
        return action
    

    def sync_script(self):
        """Creates an action that is to be send to sync all the waypoints in the flight planner to the mission planner script.
        Returns:
            Action: A sync script action.

        Returns:
            _type_: _description_
        """
        action = Action(Commands.SYNC_SCRIPT)
        return action
        
    
    def get_flightplanner_waypoints(self):
        """Requests for the waypoints from the Flightplanner tab on the connected mission planner.

        Returns:
            Action: A get_flightplanner_waypoints action.
        """
        action = Action(Commands.GET_FLIGHTPLANNER_WAYPOINTS)
        return action
    

    def arm_disarm_aircraft(self):
        if self.armed == False:
            self.armed = True
            action = Action(Commands.ARM, arm=True)
            return action
        else:
            self.armed = False
            action = Action(Commands.ARM, arm=False)
            return action

if __name__ == "__main__":
    # try:
        # host = "192.168.1.111"  # Hardcoded host IP. Can be found on the console in Mission Planner.
        # host = "172.23.80.1"
        host = raw_input("Enter IP to connect to: ")

        
        PORT = 7766  # port number of the connection.
        mp_socket = MissionPlannerSocket(host, PORT)

        # TESTING
        test_waypoints = [{"lat":-37.8238872, "long":145.0538635, "alt":0},
                            {"lat":-37.8408347, "long":145.2241516, "alt":100},
                            {"lat":-37.8411058, "long":145.2569389, "alt":100},
                            {"lat":-37.8657742, "long":145.2680969, "alt":100},
                            {"lat":-37.8818991, "long":145.2234650, "alt":100}]
        
        # mp_socket.override_waypoints(test_waypoints)
        # mp_socket.start_mission()
        # mp_socket.go_to_waypoint()
        # mp_socket.start_mission_from_waypoint(3)
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
                mp_socket.override_flightplanner_waypoints(test_waypoints)
            elif option == '2':
                mp_socket.sync_script()
            elif option == '3':
                mp_socket.override_waypoints(test_waypoints)
            elif option == '4':
                mp_socket.arm_aircraft()
            elif option == '5':
                mp_socket.get_flightplanner_waypoints()
            elif option == 'q':
                break
            else:
                print("Invalid Option.")
        mp_socket.close()
    # except Exception as e:
    #     print(e)




    
