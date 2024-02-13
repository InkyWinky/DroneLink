from __future__ import print_function, division
import socket
from CommunicationScript.MissionPlannerSocket import MissionPlannerSocket
from DronelinkHTTPServer import HTTPServerThread
from DronelinkWebSocketServerNew import WebSocketThread
import websockets
import asyncio


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
    # Create event loop object
    loop = asyncio.get_event_loop()

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
    global vision_websocket_url
    vision_websocket_url = "wss://relay.uas.unexceptional.dev/relay/images/outbound"

    # Initialise Web Socket Server for real time data transfer.
    web_socket_server = WebSocketThread(IP, mp_socket, vision_websocket_url, loop)
    print("[INFO] WebSocket Initialised on:", IP + ":" + str(8081))
    loop.run_until_complete(web_socket_server.run())

    # HTTP Server
    http_server = HTTPServerThread(IP, mp_socket, vision_websocket_url)
    loop.run_until_complete(http_server.run())
    
    print("[INFO] HTTP Server Initialised on:", IP + ":" + str(8000))

    try:
        a = input("PRESS ENTER TO STOP SERVERS\n")
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

    print("[TERMINATION] Dronelink Server Successfully Closed!")