from __future__ import division, print_function
import matplotlib.pyplot as plt
import math
class Polygon:
    def __init__(self, vertices=None):
        self.vertices = vertices
        pass

class Waypoint:
    def __init__(self):
        pass

class Point:
    def __init__(self):
        pass

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

    def generate_spline(self):
        # Find the axis of orientation that returns the fewest amount of waypoints (turns)
        #
        pass
