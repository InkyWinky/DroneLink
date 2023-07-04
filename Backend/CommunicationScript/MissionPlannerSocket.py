import socket
import threading
import json

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
        # Create Socket and connect to address
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chunk_size = 1024
        self.connect()
    
    def connect(self):
        """Connects the Socket to the host and port, if successful, a new thread will be created to handle sends and receives.
        """
        print("Attempting to connect to (" + self.HOST + ":" + str(self.PORT) + ")")
        try:
            self.s.connect((self.HOST, self.PORT))
            # Create a new thread to handle the data sent and received.
            #mp_socket_thread = threading.Thread(target=self.input_data(), args = None)
            #mp_socket_thread.start()
            #mp_socket_thread.join()
        except Exception as e:
            print(e)
            self.close()
        

    def close(self):
        """Safely closes the Socket.
        """
        self.s.sendall(bytes("quit", 'utf-8'))
        self.s.close()  # close socket
        print("Connection to (" + self.HOST + ":" + str(self.PORT) + ") was lost.")


    def input_data(self):
        """Temporary handling of sending/receiving data (asks user to input data by keyboard). 
        """
        txt_to_send = ""
        while True:
            txt_to_send = input("Enter Text to Send: ")
            self.s.sendall(bytes(txt_to_send, 'utf-8'))
            if txt_to_send == "quit":
                break
            data = self.s.recv(self.chunk_size)
            print("Data Echoed Back: " + data)
        self.close()


    def override_waypoints(self, waypoints):
        """Sends an Action to overwrite all the waypoints in mission planner.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        action = Commands.override(waypoints)
        self.s.sendall(bytes(action.serialize(), 'utf-8'))
    
    def override_flightplanner_waypoints(self, waypoints):
        """Sends an Action to overwrite all the waypoints in the flight planner GUI.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.
        """
        action = Commands.override_flightplanner(waypoints)
        self.s.sendall(bytes(action.serialize(), 'utf-8'))

    def sync_script(self):
        """Sends an Action to sync all the waypoints in the flight planner to the mission planner script.
        """
        action = Commands.sync_script()
        self.s.sendall(bytes(action.serialize(), 'utf-8'))
class Action:
    """The class that is sent from the backend connection to execute commands on the mission planner script.
    """
    def __init__(self, command):
        self.command = command
        self.waypoints = None
    

    def serialize(self):
        """Serializes the Action into a json string to be sent over the socket.

        Returns:
            str: The Action in string format. {"command":command, "waypoints":waypoints}
        """
        return json.dumps({"command":self.command, "waypoints":self.waypoints})


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

    def override(waypoints):
        """Creates an action that is to be sent to overrides all the waypoints in mission planner.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.

        Returns:
            Action: An override action with the waypoints to override with.
        """
        action = Action(Commands.OVERRIDE)
        action.waypoints = waypoints
        return action
    
    def override_flightplanner(waypoints):
        """Creates an action that is to be sent to overrides all the waypoints in the flight planner GUI.

        Args:
            waypoints (List[dict]): A list of dictionaries that contain keys: lat, long and alt.

        Returns:
            Action: An override_flightplanner action with the waypoints to override with.
        """
        action = Action(Commands.OVERRIDE_FLIGHTPLANNER)
        action.waypoints = waypoints
        return action
    
    def sync_script():
        """Creates an action that is to be send to sync all the waypoints in the flight planner to the mission planner script.
        Returns:
            Action: A sync script action.

        Returns:
            _type_: _description_
        """
        action = Action(Commands.SYNC_SCRIPT)
        return action
        


if __name__ == "__main__":
    try:
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
        option = None
        while True:
            print("--------------------------------------------------------------------------------------")
            print("[Command Selection Menu]")
            print("These Commands will be sent and executed on the Mission Planner Communication Script!")
            print("--------------------------------------------------------------------------------------")
            print("[ 1 ]. OVERRIDE FLIGHTPLANNER WAYPOINTS (Hardcoded Waypoints)")
            print("[ 2 ]. SYNC SCRIPT")
            print("[ 3 ]. OVERRIDE WAYPOINTS on Live Drone (Hardcoded waypoints)")
            print("[ q ]. Quit")
            print("--------------------------------------------------------------------------------------")

            option = input("Select Command To Execute (Enter 'q' to Quit): ")
            if option == '1':
                mp_socket.override_flightplanner_waypoints(test_waypoints)
            elif option == '2':
                mp_socket.sync_script()
            elif option == '3':
                mp_socket.override_waypoints(test_waypoints)
            elif option == 'q':
                break
            else:
                print("Invalid Option.")
        mp_socket.close()
    except Exception as e:
        print(e)




    
