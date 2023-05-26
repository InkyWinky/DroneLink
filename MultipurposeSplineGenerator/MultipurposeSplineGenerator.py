from __future__ import division, print_function
import matplotlib.pyplot as plt
import math

class Polygon:
    def __init__(self, vertices=None):
        self.vertices = vertices  # List of Point instances

class Waypoint:
    def __init__(self, x=None, y=None):
        self.coords = Point(x, y)  # Point instance that stores location of waypoint
        self.desired_exit_angle = None  # Angle in radians where "east" is zero radians and increments with the unit circle
        self.turn_direction = None  # "clockwise" or "counter_clockwise"
        self.centre_point = None  # Point instance
        self.curve_waypoints = None  # List of Point instances that are the interpolated points of the curve

class Point:
    def __init__(self, x=None, y=None):
        self.x = x  # Longitude
        self.y = y  # Latitude

class MultipurposeSplineGenerator:

    # Data (lists and boundaries)
    raw_waypoints = None  # List of rough waypoints to travel through
    spline_waypoints = None  # Generated list of Waypoint class instances that defines the interpolated search path
    search_area = None  # Polygon class instance that defines the boundary of the search area the plane will scan
    boundary = None  # Polygon class instance that defines the boundary that the path must remain in. Path can be on the boundary

    # Parameters
    minimum_turning_radius = None  # The minimum turning radius of the plane at cruise speed in metres
    boundary_resolution = None  # A factor inversely proportional to the step size that the path will adjust to avoid the boundary
    boundary_tolerance = None  # The minimum distance from the boundary the path must remain
    curve_resolution = None  # How many waypoints per metre we want

    def set_data(self, raw_waypoints=None, search_area=None, boundary=None):
        if raw_waypoints is not None:
            self.raw_waypoints = raw_waypoints
        if search_area is not None:
            self.search_area = search_area
        if boundary is not None:
            self.boundary = boundary

    def set_parameters(self, minimum_turning_radius=None, boundary_resolution=None, boundary_tolerance=None, curve_resolution=None):
        if minimum_turning_radius is not None:
            self.minimum_turning_radius = minimum_turning_radius
        if boundary_resolution is not None:
            self.boundary_resolution = boundary_resolution
        if boundary_tolerance is not None:
            self.boundary_tolerance = boundary_tolerance
        if curve_resolution is not None:
            self.curve_resolution = curve_resolution

    def generate_path(self):
        # Complete data and parameter validation checks
        validation, error_message = self.do_validation_checks()
        if validation is None:
            return validation, error_message

        # Find the axis of orientation that returns the fewest amount of waypoints (turns)
        # Method 1: Loop over multiple axes of orientation and calculate the path for each then compare which has the least turns and shortest flight time
        # Method 2: Try to estimate the number of turns and flight time for each angle then pick the most desirable

        # Find the first coordinate of the grid search. This will depend on the take-off position of the Albatross

        # Calculate points that once connected, will "search" the entire grid along with desired overlap percentage

        # Update the self.waypoints will the search grid waypoints
        pass

    def do_validation_checks(self):
        # Ensure the class instance has all the data and parameters it needs to generate a path
        validation_flag, error_message = self.validation_data_parameters()
        if validation_flag is None:
            return validation_flag, error_message

        # Check the boundary for open ends
        validation_flag, error_message = self.validation_search_area_polygon()
        if validation_flag is None:
            return validation_flag, error_message

        # Check the search area for open ends
        validation_flag, error_message = self.validation_boundary_polygon()
        if validation_flag is None:
            return validation_flag, error_message

    def validation_data_parameters(self):
        if self.raw_waypoints is None or self.search_area is None or self.minimum_turning_radius is None or self.curve_resolution is None:
            return None, "Not all essential data or parameters are set in the class instance"

    def validation_boundary_polygon(self):
        if self.boundary is not None:
            for index in range(len(self.boundary) - 1):
                if self.boundary[index] != self.boundary[index + 1]:
                    return None, "The boundary polygon is not closed"

    def validation_search_area_polygon(self):
        if self.search_area is not None:
            for index in range(len(self.search_area) - 1):
                if self.search_area[index] != self.search_area[index + 1]:
                    return None, "The search area polygon is not closed"

    def calculate_best_axis_of_orientation(self):
        pass

    def calculate_first_coordinate(self):
        pass

    def calculate_waypoints(self):
        pass
