# This file receives messages published by publish.py and any messages from the SITL environment.

from CubeConnection import CubeConnection
from mav_enums import CommandResults, MUASComponentID, MUASCommands, WadjetCommands
import time

# connection_string is the string used to define the connection to the network. The current connection string here is the string required to connect to SITL simulation
# environment.
# Link to connection string examples: https://mavlink.io/zh/mavgen_python/#connection_string
connection_string = "tcp:127.0.0.1:5762" # Port 5762 is serial port 1 on the SITL simulated cube.

# Set the source mavlink system as 1 (This will always be the case for us, unless we plan on having two albatrosses running on the same network)
cube_connection = CubeConnection(connection_string, system=1, component=MUASComponentID.WADJET)


# Setting our filters which are the message types we want to receive as obtained from here: https://mavlink.io/en/messages/common.html
filters = ["DEBUG_VECT", "STATUSTEXT"]

while True:
    # Pull the next message. This is a BLOCKING operation by default, that is, it waits until it receives ONE of the message specified then returns the message here,
    # specify tag with 'blocking=False'. If this is a time sensitive task, it is best offload this into a separate thread.

    # Receive and print message
    msg = cube_connection.next_message(filters=filters, blocking=True)
    print(msg)

    # Example on receiving and handling commands
    msg = cube_connection.next_message(filters="COMMAND_INT", blocking=True)
    if msg.command == MUASCommands.WADJET and msg.target_component == MUASComponentID.WADJET:  # Check if this command is for us
        print(WadjetCommands(msg.param1).name)
        # Send acknowledgement of command
        cube_connection.send_command_acknowledgement(msg.command, CommandResults.MAV_RESULT_CANCELLED)
    else:
        continue


