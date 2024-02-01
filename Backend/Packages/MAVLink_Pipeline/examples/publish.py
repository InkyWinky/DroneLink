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

cube_connection = CubeConnection(connection_string, system=1, component=MUASComponentID.MISSION_MANAGEMENT)     # This script will send and receive commands as MISSION MANAGEMENT.

# This is the physical connection that we need for sending data and texts
connection = cube_connection.connection
i = 0
while True:
    # create the text
    text = f"Roll a dice: {random.randint(1, 6)} flip a coin: {random.randint(0, 1)}"

    # send message to the GCS
    # Note that statustext should be avoided as it uses a lot of bandwidth.
    connection.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_NOTICE, text.encode())

    # You can send any message that is detailed here: https://mavlink.io/en/messages/common.html
    # Follow the message type in lowercase with _send. Example below.
    print(i)
    # Lidar send
    curr_time = cube_connection.get_time()
    connection.mav.named_value_int_send(i, "LIDAR".encode(), random.randint(1, 10))

    # Geolocation send
    connection.mav.debug_vect_send("GEOTAG_GPS".encode(), i, 0.1234567, 0.1234567, 15)
    connection.mav.debug_vect_send("GEOTAG_BOX".encode(), i, 0.135, 0.674, 0.09)

    # Send command to WADJET to go into NEUTRAL MODE.
    connection.mav.command_int_send(1, MUASComponentID.WADJET, 0, MUASCommands.WADJET, 0, 0, WadjetCommands.NEUTRAL_MODE, 0, 0, 0, 0, 0, 0)
    i += 1
    # sleep a bit
    time.sleep(2)
    msg = cube_connection.next_message(filters="COMMAND_ACK", blocking=True)
    print(CommandResults(msg.result).name)
