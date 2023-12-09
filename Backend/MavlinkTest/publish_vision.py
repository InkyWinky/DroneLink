from pymavlink import mavutil
from CubeConnection import CubeConnection
import time
import random
from mav_enums import CommandResults, MUASComponentID, MUASCommands, WadjetCommands

# connection_string is the string used to define the connection to the network. The current connection string here is the string required to connect to SITL simulation
# environment.
# Link to connection string examples: https://mavlink.io/zh/mavgen_python/#connection_string
connection_string = "tcp:127.0.0.1:5763" # Port 5763 is serial port 2 on the SITL simulated cube.

# Set the source mavlink system as 1 (This will always be the case for us, unless we plan on having two albatrosses running on the same network)

cube_connection = CubeConnection(connection_string, system=1, component=MUASComponentID.VISION)     # This script will send and receive commands as MISSION MANAGEMENT.

# This is the physical connection that we need for sending data and texts
connection = cube_connection.connection
i = 0
while True:

    # You can send any message that is detailed here: https://mavlink.io/en/messages/common.html
    # Follow the message type in lowercase with _send. Example below.
    print(i)

    # Geolocation send
    connection.mav.debug_vect_send("GEOTAG_GPS".encode(), i, random.random(), random.random(), 15)
    connection.mav.debug_vect_send("GEOTAG_BOX".encode(), i, random.random(), random.random(), random.random())

    i += 1
    # sleep a bit
    time.sleep(2)

