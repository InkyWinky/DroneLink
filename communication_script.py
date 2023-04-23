"""
Mission Planner Communication Script
Creates a communication link between the Backend Server and Mission Planner.
Utilises MavLink and is run as a Mission Planner Script.

Script Usage
From Mission Planner Home, navigate to "Simulation" -> "Plane" -> "Stable".
On the left side, navigate to "Scripts" -> "Select Script" -> "Upload" ->
 -> "Run Script"
"""

print("Importing Dependencies...")
import socket
import clr
clr.AddReference("MissionPlanner")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink")
import MAVLink
print("Starting Script...")



"""
Function: waypoint_test
Description: Sets the current mission to hard-coded waypoints.
Inputs: None
Outputs: None
"""
def waypoint_test():
    id = int(MAVLink.MAV_CMD.WAYPOINT) # id_mav_cmd for waypoints

    home = Locationwp().Set(-35.3352932, 148.6175537, 0, id)

    takeoff = Locationwp()
    Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.TAKEOFF))
    Locationwp.p1.SetValue(takeoff, 15)
    Locationwp.alt.SetValue(takeoff, 50)

    wp1 = Locationwp().Set(-37.8408347, 145.2241516, 100, id)
    wp2 = Locationwp().Set(-37.8411058, 145.2569389, 100, id)
    wp3 = Locationwp().Set(-37.8657742, 145.2680969, 100, id)
    wp4 = Locationwp().Set(-37.8818991, 145.2234650, 100, id)

    MAV.setWPTotal(6)
    MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(takeoff, 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp1, 2, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp2, 3, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp3, 4, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWP(wp4, 5, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
    MAV.setWPACK()



# NOTE: Script is run as a module and not as __main__.
waypoint_test()
print("Script Terminated!")

