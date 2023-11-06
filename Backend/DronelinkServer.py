from __future__ import print_function, division
import socket
from CommunicationScript.MissionPlannerSocket import MissionPlannerSocket
from DronelinkHTTPServer import HTTPServerThread
from DronelinkWebSocketServer import WebSocketThread
        

def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

if __name__ == "__main__":

    # Initialise Mission Planner Socket.
    MP_PORT = 7766
    global mp_socket
    mp_socket = MissionPlannerSocket(MP_PORT)
    print("[INFO] Mission Planner Socket Initialised")

    # Get the IP of the device running the backend.
    try:
        hostname = socket.getfqdn()
        addr = get_ip() # min(socket.gethostbyname_ex(hostname)[2])
    except Exception:
        addr = "127.0.0.1"
    global IP
    IP = addr

    # Initialise Web Socket Server for real time data transfer.
    clients = []
    clientData = []
    web_socket_server = WebSocketThread(IP, mp_socket)
    web_socket_server.start()
    print("[INFO] WebSocket Initialised on:", IP + ":" + str(8081))

    # HTTP Server
    http_server = HTTPServerThread(IP, mp_socket)
    http_server.start()
    print("[INFO] HTTP Server Initialised on:", IP + ":" + str(8000))

    try:
        a = raw_input("PRESS ENTER TO STOP SERVERS\n")
    finally:
        try:
            web_socket_server.close()
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
    
    # Wait until all threads are closed.
    web_socket_server.join()
    http_server.join()
    
    print("[TERMINATION] Dronelink Server Successfully Closed!")