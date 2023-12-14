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

cube_connection = CubeConnection(connection_string, system=1, component=MUASComponentID.WADJET)     # This script will send and receive commands as MISSION MANAGEMENT.

# This is the physical connection that we need for sending data and texts
connection = cube_connection.connection
i = 0
while True:
    # You can send any message that is detailed here: https://mavlink.io/en/messages/common.html
    # Follow the message type in lowercase with _send. Example below.
    print(i)

    # Lifeline send
    connection.mav.named_value_float_send(i, "LFL_STATUS".encode(), 800)
    connection.mav.named_value_float_send(i, "LFL_DIST".encode(), random.random())
    connection.mav.named_value_float_send(i, "LFL_VEL".encode(), random.random() * 10)

    # Send command to WADJET to go into NEUTRAL MODE.
    # connection.mav.command_int_send(1, MUASComponentID.MISSION_MANAGEMENT, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    i += 1
    # sleep a bit
    time.sleep(2)
    # msg = cube_connection.next_message(filters="COMMAND_ACK", blocking=True)
    # print(CommandResults(msg.result).name)
