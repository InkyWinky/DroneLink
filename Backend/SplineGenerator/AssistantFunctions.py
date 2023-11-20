"""
These functions are useful for geometry problems or 2D and 3D path planning.

Written by Nicholas Dellaportas.
"""

import math

class Coord:
    def __init__(self, lat=None, lon=None):
        self.lat = lat  # Latitude
        self.lon = lon  # Longitude

    def magnitude(self, point=None):
        if point is None:
            return math.sqrt(self.lon ** 2 + self.lat ** 2)
        else:
            return math.sqrt(point.lon ** 2 + point.lat ** 2)

    def dot(self, point_2):
        return self.lon * point_2.lon + self.lat * point_2.lat

    def multiply(self, scalar):
        return Coord(lon=self.lon * scalar, lat=self.lat * scalar)

    def equals(self, point=None):
        if self.lon == point.lon and self.lat == point.lat:
            return True
        return False

def distance_between_points(point_1=None, point_2=None):
    return math.sqrt((point_1.lon - point_2.lon) ** 2 + (point_1.lat - point_2.lat) ** 2)

def create_point(point=None, dist=None, angle=None):
    return Coord(lon=point.lon + dist * math.cos(angle), lat=point.lat + dist * math.sin(angle))

def general_curve_interpolation(start_point=None, start_angle=None, end_point=None, end_angle=None, centre_point=None, turn_direction=None, number_of_turns=None, radius=None, curve_resolution=None):
    """
    Function capable of returning the points along an arc multiple ways.
    The start or end points of the curve can be used or the start and end angle with respect to the positive x-axis can be used. A combination
    of the two can also be used.
    """
    # If the centre point is not given, create it using other variables. Only if number_of_turns is None though.
    if centre_point is None and number_of_turns is None:
        # Check that both points are given as they should be
        if start_point is None or end_point is None:
            raise ValueError("Not enough information provided to interpolate the curve.")

        # Find the longitude and latitude component differences
        distance = distance_between_points(start_point, end_point)
        h = math.sqrt(radius * radius - 1)

        lon_diff = end_point.lon - start_point.lon
        lat_diff = end_point.lat - start_point.lat

        solution_1 = Coord(start_point.lon + (h / distance) * lat_diff + (1 / distance) * lon_diff,
                           start_point.lat - (h / distance) * lon_diff + (1 / distance) * lat_diff)

        solution_2 = Coord(start_point.lon - (h / distance) * lat_diff + (1 / distance) * lon_diff,
                           start_point.lat + (h / distance) * lon_diff + (1 / distance) * lat_diff)

        if turn_direction == "clockwise":
            centre_point = solution_1
        else:
            centre_point = solution_2

    # If the start or end points are given, convert them into angles
    if start_point is not None:
        start_angle = math.atan2(start_point.lat - centre_point.lat, start_point.lon - centre_point.lon)

    if end_point is not None:
        end_angle = math.atan2(end_point.lat - centre_point.lat, end_point.lon - centre_point.lon)

    # Find the amount of angle that needs to be interpolated
    if number_of_turns is None:
        if turn_direction == "clockwise":
            angle_difference = start_angle - end_angle
        else:
            angle_difference = end_angle - start_angle
    else:
        angle_difference = 2 * math.pi * number_of_turns

    # Calculate the number of points along the arc
    arc_length = angle_difference * radius
    number_of_points = int(1 + math.ceil(arc_length * curve_resolution))

    # Find the angle step required to exactly achieve the number of points
    angle_step = angle_difference / number_of_points

    # If the direction is clockwise, make the angle step negative
    if turn_direction == "clockwise":
        angle_step *= -1

    # Create the points along the curve
    curve_points = []
    for index in range(number_of_points):
        current_angle = start_angle + index * angle_step
        new_point = create_point(centre_point, radius, current_angle)
        curve_points.append(new_point)

    return curve_points

