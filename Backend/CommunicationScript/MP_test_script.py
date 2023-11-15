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
from System import UInt16
print("[INFO] Starting Script...")
from MAVLink import mavlink_command_int_t

print(MissionPlanner.MainV2.comPort) # MainV2.comPort is an instance of the MAVLinkInterface that Mission Planner is actively using
# For the source code: https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/ExtLibs/ArduPilot/Mavlink/MAVLinkInterface.cs

# Example 2: send command_long 
# https://github.com/ArduPilot/MissionPlanner/blob/c69793a6abaf97fc17b90cc099cbfd391c16dced/Scripts/example2.py
print("sysidcurrent: " + str(MAV.sysidcurrent) + " | compidcurrent: " + str(MAV.compidcurrent))
print("MavList: ", MAV.MAVlist)
commandInt = mavlink_command_int_t()
mavlink_command_int_t.target_system.SetValue(commandInt, MAV.sysidcurrent)
mavlink_command_int_t.target_component.SetValue(commandInt,MAV.compidcurrent)
mavlink_command_int_t.param1.SetValue(commandInt, 1)
mavlink_command_int_t.param2.SetValue(commandInt, 21196)
mavlink_command_int_t.command.SetValue(commandInt, MAVLink.MAV_CMD.COMPONENT_ARM_DISARM.value__)

# command , target sysid, target compid    used to keep track of the remote state
MAV.sendPacket(commandInt, MAV.sysidcurrent, MAV.compidcurrent)
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