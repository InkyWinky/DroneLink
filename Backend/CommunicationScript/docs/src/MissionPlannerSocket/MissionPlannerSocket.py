import socket
import threading

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
        self.connect()
    
    def connect(self):
        """Connects the Socket to the host and port, if successful, a new thread will be created to handle sends and receives.
        """
        print(f"Attempting to connect to ({self.HOST}, {self.PORT})")
        try:
            self.s.connect((self.HOST, self.PORT))
            # Create a new thread to handle the data sent and received.
            mp_socket_thread = threading.Thread(target=mp_socket.input_data(), args = None)
            mp_socket_thread.start()
            mp_socket_thread.join()
        except Exception as e:
            print(e)
        

    def close(self):
        """Safely closes the Socket.
        """
        self.s.close()  # close socket
        print(f"Connection to ({self.HOST}, {self.PORT}) was lost.")
        

    def input_data(self):
        """Temporary handling of sending/receiving data (asks user to input data by keyboard). 
        """
        txt_to_send = ""
        while True:
            txt_to_send = input("Enter Text to Send: ")
            self.s.sendall(bytes(txt_to_send, 'utf-8'))
            if txt_to_send == "quit":
                break
            data = self.s.recv(1024)
            print("Data Echoed Back: ", data)
        self.close()


if __name__ == "__main__":
    host = "192.168.1.111"  # Hardcoded host IP. Can be found on the console in Mission Planner.
    PORT = 7766  # port number of the connection.
    mp_socket = MissionPlannerSocket(host, PORT)
    
