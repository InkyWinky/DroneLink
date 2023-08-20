import socket
import threading
import json
import time

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


    def initialise_dronelink(self, ip):
        self.HOST = ip
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
                        # pass
                        try:
                            self.live_data_mutex.acquire()
                            self.live_data = decoded_data["data"]
                            self.live_data_mutex.release()
                        except Exception as e:
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
        if self.s is not None:
            self.s.sendall(bytes("quit"))
            self.s.shutdown(1)
            self.s.close()  # close socket
            self.quit = True
            print("[INFO] Connection to (" + self.HOST + ":" + str(self.PORT) + ") was lost.")

        

    def override_waypoints(self, waypoints):
        """Sends a command to overwrite all the waypoints in mission planner.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        data = json.dumps({"command":self.COMMANDS.OVERRIDE, "waypoints": waypoints})
        self.s.sendall(data)
    
    
    def override_flightplanner_waypoints(self, waypoints, takeoff_alt):
        """Sends a command to overwrite all the waypoints in the flight planner GUI.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        data = json.dumps({"command":self.COMMANDS.OVERRIDE_FLIGHTPLANNER, "waypoints": waypoints, "takeoff_alt":takeoff_alt})
        self.s.sendall(data)


    def sync_script(self):
        """Sends a command to sync all the waypoints live on the drone to the mission planner script.
        """
        data = json.dumps({"command":self.COMMANDS.SYNC_SCRIPT})
        self.s.sendall(data)

    def toggle_arm_aircraft(self):
        """Sends a command to toggle the arming state of the drone
        """
        data = json.dumps({"command":self.COMMANDS.TOGGLE_ARM})
        self.s.sendall(data)


    def get_flightplanner_waypoints(self):
        """Sends a command to get all the waypoints in the flight planner.
        """
        data = json.dumps({"command":self.COMMANDS.GET_FLIGHTPLANNER_WAYPOINTS})
        self.s.sendall(data)

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
    

if __name__ == "__main__":
    # try:
        # host = "192.168.1.111"  # Hardcoded host IP. Can be found on the console in Mission Planner.
        # host = "172.23.80.1"
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
                mp_socket.toggle_arm_aircraft()
            elif option == '5':
                mp_socket.get_flightplanner_waypoints()
            elif option == 'q':
                break
            else:
                print("Invalid Option.")
        mp_socket.close()
    # except Exception as e:
    #     print(e)




    
