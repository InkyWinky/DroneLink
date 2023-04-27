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

class MissionManager:
    """
    Constructor
    Input:
        sync: bool 
                True - gets the waypoints from Mission Planner on startup.
                False - starts waypoints as an empty list, Mission Planner may have waypoints.
    """
    def __init__(self, sync=True):
        self.id = int(MAVLink.MAV_CMD.WAYPOINT)  # id_mav_cmd for waypoints
        self.waypoint_count = 0
        self.waypoints = []
        if sync:
            self.sync()  # get initial waypoints from mission planner

    """ 
    Custom print str
    Called by using print(MissionManager()) 
    """
    def __str__(self):
        if self.waypoint_count == 0:
            return "Waypoints ---> Empty"
        
        txt = "----------------------------------------------\nWaypoints\n [num]. latitude, longitude, altitude\n"
        for i in range(self.waypoint_count):
            wp = self.waypoints[i]
            txt += "[" + str(i) + "]. " + str(wp.lat) + ", " + str(wp.lng) + ", " + str(wp.alt) + "\n"
        return txt + "----------------------------------------------"
    
    """ 
    Custom get item 
    """
    def __getitem__(self, index):
        if index < self.waypoint_count:
            return self.waypoints[index]
        return None
    
    """ 
    Custom set item 
    """
    def __setitem__(self, index, waypoint):
        if index < self.waypoint_count:
            self.waypoints[index] = waypoint
        else:
            print("ERROR: Setting Waypoint at index " + str(index) + " was out of bounds.")
    
    """ 
    Syncs all the waypoints in Mission Planner to waypoints list (overrides any previous changes)
    """
    def sync(self):
        self.waypoint_count = MAV.getWPCount()
        self.waypoints = [MAV.getWP(index) for index in range(MAV.getWPCount())]

    """ 
    Adds a waypoint to the end of the route 
    """
    def append(self, waypoint):
        # Update waypoint count
        self.waypoint_count += 1
        # Append to class list and Mission planner
        self.waypoints.append(waypoint)

    """ 
    Inserts a waypoint at a certain index. (not very efficient) 
    """
    def insert(self, index, waypoint):
        # Update waypoint count
        self.waypoint_count += 1
        # Insert into class list and Mission Planner
        self.waypoints.insert(index, waypoint)
    
    """
    Updates Mission Planner on the modified waypoints
    """
    def update(self):
        MAV.setWPTotal(len(self.waypoints))
        for i in range(len(self.waypoints)):
            MAV.setWP(self.waypoints[i], i, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

        MAV.setWPACK()  # Send waypoint ACK
        self.__set_home(self.waypoints[0])  # Set the home waypoint as the first waypoint
    
    """
    Creates a waypoint
    The object returned is a Locationwp. This is an object part of MAVLink/Mission Planner
    """
    def create_wp(self, lat, lng, alt):
        return Locationwp().Set(lat, lng, alt, self.id)
    
    """
    Alters lat, lng and alt of a waypoint via index and sets it into Mission Planner
    """
    def set_waypoint(self, lat, lng, alt, index):
        wp = self[index]
        Locationwp.lat.SetValue(wp, lat)
        Locationwp.lng.SetValue(wp, lng)
        Locationwp.alt.SetValue(wp, alt)
        self[index] = wp

    
    """
    Alters lat of a waypoint via index and sets it into Mission Planner
    """
    def set_lat(self, index, value):
        wp = self[index]
        Locationwp.lat.SetValue(wp, value)
        self[index] = wp

    """
    Alters lng of a waypoint via index and sets it into Mission Planner
    """
    def set_lng(self, index, value):
        wp = self[index]
        Locationwp.lng.SetValue(wp, value)
        self[index] = wp

    """
    Alters alt of a waypoint via index and sets it into Mission Planner
    """
    def set_alt(self, index, value):
        wp = self[index]
        Locationwp.alt.SetValue(wp, value)
        self[index] = wp
    

    """
    Sets the waypoint to go to in guided mode
    """
    def target_waypoint(self, index):
        MAV.setGuidedModeWP(self.waypoints[index])

    """
    Sets the home waypoint (NOTE: THIS SHOULD BE INDEX=0 IN THE WAYPOINTS LIST)
    Private Function
    """
    def __set_home(self, waypoint):
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME, 0, 0, 0, 0, waypoint.lat, waypoint.lng, waypoint.alt)
        self.waypoints[0] = waypoint


"""
Function: waypoint_mavlink_test
Description: Sets the current mission to hard-coded waypoints using MAVLink functions.
Inputs: None
Outputs: None
"""
def waypoint_mavlink_test():
    id = int(MAVLink.MAV_CMD.WAYPOINT) # id_mav_cmd for waypoints
    MAV.doCommand
    home = Locationwp().Set(-37.8238872, 145.0538635, 0, id)

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

    # Set Home waypoint
    MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME, 0, 0, 0, 0, -37.8238872, 145.0538635, 0)


"""
Function: waypoint_manager_test
Description: Adds hard-coded waypoints to the current mission using the Mission Manager Class.
Inputs: None
Outputs: None
"""
def waypoint_manager_test():
    mm = MissionManager(sync=False)  # Sync is set to False so that we can overwrite existing waypoints

    print("After Syncing")
    print(mm)
    home = mm.create_wp(-37.8238872, 145.0538635, 0)

    takeoff = Locationwp()
    Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.TAKEOFF))
    Locationwp.p1.SetValue(takeoff, 15)
    Locationwp.alt.SetValue(takeoff, 50)

    wp1 = mm.create_wp(-37.8408347, 145.2241516, 100)
    wp2 = mm.create_wp(-37.8411058, 145.2569389, 100)
    wp3 = mm.create_wp(-37.8657742, 145.2680969, 100)
    wp4 = mm.create_wp(-37.8818991, 145.2234650, 100)

    mm.append(home)
    mm.append(takeoff)
    mm.append(wp1)
    mm.append(wp2)
    mm.append(wp3)
    mm.append(wp4)
    mm.update()
    print("After Adding")
    print(mm)

    # Sleep for 5 seconds before editing waypoint 2
    print("Sleeping for 5 seconds")
    Script.Sleep(5000)
    print("Changing waypoint 2")
    mm.set_waypoint(-37.7202198, 145.1486206, 100, 2)
    mm.update()

    #
    print("Set Guided Mode Waypoint to: wp3 (index 4)")
    mm.target_waypoint(4)
    
    # Sleep for 5 seconds before adding a new waypoint
    print("Sleeping for 5 seconds")
    Script.Sleep(5000)
    print("Adding a waypoint")
    wp5 = mm.create_wp(-37.9154926, 145.1170349, 100)
    mm.append(wp5)
    mm.update()

# NOTE: Script is run as a module and not as __main__.

#waypoint_mavlink_test()
waypoint_manager_test()

print("Script Terminated!")

