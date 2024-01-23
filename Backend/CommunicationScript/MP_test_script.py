print("[INFO] Importing Dependencies...")

# Importing Python dependencies
# import sys
# sys.path.append(r"c:/python27/lib")
import socket
import json
import clr
import threading
import gc
import time
import datetime

# Importing MissionPlanner dependencies
clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")
from MissionPlanner.Utilities import Locationwp, WaypointFile
# clr.AddReference("MAVLink")
import MAVLink
from MAVLink import MAV_CMD

# Importing C# List primitive dependency 
clr.AddReference('System')
from System.Collections.Generic import List
from System import UInt16, Func
print("[INFO] Starting Script...")
from MAVLink import mavlink_command_int_t

print(MissionPlanner.MainV2.comPort) # MainV2.comPort is an instance of the MAVLinkInterface that Mission Planner is actively using
# For the source code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/ExtLibs/ArduPilot/Mavlink/MAVLinkInterface.cs

def handle_message_packet(o, message):
    """Handles any MAVLink message packets received, and prints if they are command_int or debug_vect messages
    architecture taken from:
        - https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/Scripts/example2.py
        - https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/Scripts/example10.py

    Args:
        MAVLink.MAVLinkMessage message: The MAVLink message packet received
    """

    # if component id corresponds to payload
    print("WOW")
    try:
        if message.msg_id == MAVLink.MAVLINK_MSG_ID.COMMAND_INT.value__:
            print("HELP")
            print(message)
        # if message.msgid == 250: # debug_vect
        #     if message.name == "GEOTAG_GPS":
        #         target_lat = message.x
        #         target_lon = message.y
        #         target_height = message.z 
        #     elif message.name == "GEOTAG_BOX":
        #         # 3 floats represent bounding box coords
        #         box_x = int(message.x)
        #         box_y = int(message.y)
        #         box_h = int(message.z)
        # elif message.msgid == 75 and message.compid == 172: # command_int specifying MM
        #         print("[TIME TO CELEBRATE]")
        #         print(bytes(message.data))
        # else:
        #     print("Unknown Message: " + message)

    except Exception as e:
        print("[ERROR] " + e)
    return True
    
def subscribe_success(message):
    """ Callback function called if SubscribeToPacketType succeeds, and prints the message data

    Args:
        MAVLink.MAVLinkMessage message: The MAVLink message packet received
    """
    print("[MESSAGE] Successfully subscribed to command int")
    print(message.data)
    return True

def OtherMethod(message):
    print("got HB")
    return True

def subscribe_to_mavlink_msg():
    """Function to subscribe to command_int MAVLink messages (enum value: 75) """
    # subscribe to command_ints
    # sub = MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.HEARTBEAT.value__, Func[MAVLink.MAVLinkMessage, bool] (OtherMethod))
    sub_command_int = MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.COMMAND_INT, Func[MAVLink.MAVLinkMessage, bool] (handle_message_packet))
    sub2 = MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.STATUSTEXT, Func[MAVLink.MAVLinkMessage,
                                 bool] (handle_message_packet))
    # subscribe to debug_vects
    # sub_debug_vect = MAV.SubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.DEBUG_VECT.value__, Func[MAVLink.MAVLinkMessage, bool] (subscribe_success))

    #  to unsubscribe: MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.COMMAND_INT.value__, sub);
    #  to unsubscribe: MAV.UnSubscribeToPacketType(MAVLink.MAVLINK_MSG_ID.DEBUG_VECT.value__, sub);
    # MAV.OnPacketReceived += handle_message_packet

# subscribe_to_mavlink_msg() # subscribe to debug_vects and command_ints
# Example 2: send command_long 
# https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/Scripts/example2.py
print("sysidcurrent: " + str(MAV.sysidcurrent) + " | compidcurrent: " + str(MAV.compidcurrent))
# print("MavList: ", MAV.MAVlist)
while True:
    # response = Script.recv_match(type='COMMAND_INT', blocking=False)
    # print("Response: " + response)
    # if response is not None:
    #     print("HI")

    # commandInt = mavlink_command_int_t()
    # mavlink_command_int_t.target_system.SetValue(commandInt, 1)
    # mavlink_command_int_t.target_component.SetValue(commandInt, 169)
    # mavlink_command_int_t.param1.SetValue(commandInt, 1)
    # mavlink_command_int_t.param2.SetValue(commandInt, 21196)
    # mavlink_command_int_t.command.SetValue(commandInt, 976)# MAVLink.MAV_CMD.COMPONENT_ARM_DISARM.value__)
    # # command , target sysid, target compid    used to keep track of the remote state
    # MAV.sendPacket(commandInt, 1, 169)
    # print("SENT!")

    Script.Sleep(1000)
print("DONE")
# Example 10: Subscribe to Packet Type
# https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/Scripts/example10.py

# print(MissionPlanner.instance.MAVLinkInterface)
# id = int(MAVLink.MAV_CMD.WAYPOINT)
# wp1 = Locationwp().Set(-37.8408347, 145.2241516, 100, id)
# wp2 = Locationwp().Set(-37.8411058, 145.2569389, 100, id)
# wp3 = Locationwp().Set(-37.8657742, 145.2680969, 100, id)
# wp4 = Locationwp().Set(-37.8818991, 145.2234650, 100, id)

# FlightPlanner = MissionPlanner.MainV2.instance.FlightPlanner
# FlightPlanner.WPtoScreen(List[Locationwp]([wp1, wp2, wp3, wp4]))
# FlightPlanner().AddWPToMap(-37.8408347, 145.2241516, 100)
# print(flightPlanner.GetCommandList())
# MissionPlanner.MainV2.FlightPlanner.WPtoScreen(List[Locationwp]([wp1, wp2, wp3, wp4]))
# MissionPlanner.MainV2.instance.FlightPlanner.AddWPToMap(-37.8408347, 145.2241516, 100)
# MissionPlanner.MainV2.instance.FlightPlanner.AddWPToMap(-37.8411058, 145.2569389, 100)
# flightPlanner.readQGC110wpfile('./test.waypoints')

# print(MissionPlanner.MainV2.instance.FlightPlanner.Commands.Rows)
# MissionPlanner.MainV2.instance.FlightPlanner.AddWPToMap(lat, lng, alt)
# MissionPlanner.MainV2.instance.FlightPlanner.AddCommand(cmd, p1, p2, p3, p4, x, y, z, tag=null)
# MissionPlanner.MainV2.instance.FlightPlanner.InsertCommand(index, cmd, p1, p2, p3, p4, x, u, z, tag)
# MissionPlanner.MainV2.instance.FlightPlanner.readQGC110wpfile('file location')
# MissionPlanner.MainV2.instance.FlightPlanner.WPtoScreen(List[Locationwp]([wp1, wp1, wp2, wp3, wp4]))
# print(FlightPlanner.Commands.Rows.Count, FlightPlanner.Commands.Rows[0].Cells.Count)
# print(FlightPlanner.Commands.Rows[0].Cells)
# print(FlightPlanner.Commands.Rows[0].Cells[0].Value) # Command as a string
# print(FlightPlanner.Commands.Rows[0].Cells[1].Value) # param 1
# print(FlightPlanner.Commands.Rows[0].Cells[2].Value) # param 2
# print(FlightPlanner.Commands.Rows[0].Cells[3].Value) # param 3
# print(FlightPlanner.Commands.Rows[0].Cells[4].Value) # param 4
# print(FlightPlanner.Commands.Rows[0].Cells[5].Value) # Lat
# print(FlightPlanner.Commands.Rows[0].Cells[6].Value) # Lng
# print(FlightPlanner.Commands.Rows[0].Cells[7].Value) # Alt
# print(FlightPlanner.Commands.Rows[0].Cells[8].Value) #
# print(FlightPlanner.Commands.Rows[0].Cells[9].Value) #
# print(FlightPlanner.Commands.Rows[0].Cells[10].Value) #
# print(FlightPlanner.Commands.Rows[0].Cells[11].Value) #
# print(FlightPlanner.Commands.Rows[0].Cells[12].Value) #
# print(FlightPlanner.Commands.Rows[0].Cells[13].Value) # X
# print(FlightPlanner.Commands.Rows[0].Cells[14].Value) # Up btn
# print(FlightPlanner.Commands.Rows[0].Cells[15].Value) # Down btn
# print(FlightPlanner.Commands.Rows[0].Cells[16].Value) # Grad %
# print(FlightPlanner.Commands.Rows[0].Cells[17].Value) # Angle
# print(FlightPlanner.Commands.Rows[0].Cells[18].Value) # Dist
# print(FlightPlanner.Commands.Rows[0].Cells[19].Value) # AZ

# print(MissionPlanner.Plugin.GetWPs())
# print(MissionPlanner.Plugin.PluginHost.GetWPs())
# print(int(MAVLink.MAV_CMD.WAYPOINT)) # 16