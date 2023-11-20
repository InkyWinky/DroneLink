from __future__ import division, print_function
import math
import matplotlib.pyplot as plt
from PathGenerator import *
from SearchPathGenerator import Coord, Polygon
pi = math.pi

class FlyToCircleTarget:

    def __init__(self):
        # Input
        self.existing_path = None  # List of Coord classes that outline the path the plane is currently on
        self.current_path_index = None  # Index of the existing path that shows the previous waypoint the plane has travelled through
        self.plane_location = None  # Coord of plane
        self.plane_bearing = None  # Bearing of the plane when the pilot wants to go to the target
        self.target_location = None  # Coord of target
        self.turn_radius = None  # Turn radius of the plane
        self.target_circle_radius = None  # Radius to circle the target at
        self.minimum_distance_to_start = None  # Minimum distance along the existing before the plane starts turning
        self.times_to_circle = None  # Number of times to circle the target
        self.curve_resolution = None  # The number of waypoints per metre

        # Intermediate
        self.start_point = None  # The first point of the turn towards the target
        self.start_bearing = None  # Bearing of plane at the start of the turn
        self.target_rotation_direction = None  # Direction the plane will rotate around the target
        self.target_circle_start_point = None  # First point the plane will touch on the target circle
        self.path_points = None  # The Coord class list of path points

        # Output
        self.formatted_points = None  # A returnable format for the generated spline

    def set_parameters(self, plane_location=None, plane_bearing=None, target_location=None, turn_radius=None, target_circle_radius=None, minimum_distance_to_start=None, times_to_circle=None, curve_resolution=None):
        self.plane_location = plane_location
        self.plane_bearing = plane_bearing
        self.target_location = target_location
        scaling_factor = 111320 / math.cos(self.plane_location.lat)
        self.turn_radius = turn_radius / scaling_factor
        self.target_circle_radius = target_circle_radius / scaling_factor
        self.minimum_distance_to_start = minimum_distance_to_start / scaling_factor
        self.times_to_circle = times_to_circle
        self.curve_resolution = curve_resolution * scaling_factor

    def set_data(self):
        pass

    def set_existing_waypoints(self, coord_dictionary):
        coords = []
        for coord in coord_dictionary:
            new_coord = Coord(lat=coord["lat"], lon=coord["lon"])
            coords.append(new_coord)

        self.existing_path = coords

    def get_waypoints(self):
        """
                Call this function to get a dictionary of every point in the path. The format is as follows:
                [{"long": 101.24, "lat": 62.76, "alt": 100}, {"long": 98.64, "lat": 65.22, "alt": 100}, ...]
        """
        dict_list = []

        for point in self.path_points:
            new_dict_entry = {"lon": point.lon, "lat": point.lat, "alt": 100}
            dict_list.append(new_dict_entry)

        return dict_list

    def generate_path(self):
        """
        Generates a path from the current position of the plane to the closest tangent point of a circle centred at the target with desired radius.
        Returns a list of dictionary points that the plane can immediately start following.
        """
        # Initial checks

        # Parameter manipulation to be in a decimal degree compatible format

        # Create points for path
        self.path_points = self.generate_path_points()

        # Final checks

        # Return points in dictionary format
        return self.get_waypoints()

    def generate_path_points(self):
        # Create points for turn and towards circle start
        turn_points = self.generate_turn_points()

        # Create points for circling the target
        circle_points = self.generate_circle_points()

        # Return the joined points
        turn_points.extend(circle_points)
        return turn_points

    def generate_circle_points(self):
        # Get the points from a general interpolation
        circle_points = general_curve_interpolation_v2(start_point=self.target_circle_start_point, centre_point=self.target_location, turn_direction=self.target_rotation_direction, number_of_turns=self.times_to_circle, radius=self.target_circle_radius, curve_resolution=self.curve_resolution)
        return circle_points

    def generate_turn_points(self):
        # Determine start point for the turn
        self.start_point = self.turn_points_determine_start_point()

        # Find turn points
        turn_points = self.turn_points_generate_points_to_target_radius()

        # Create turn points complete list
        turn_points.insert(0, self.start_point)
        return turn_points

    def turn_points_determine_start_point(self):
        # Check if a start bearing and start point were included
        if self.plane_location is not None and self.plane_bearing is not None:
            self.start_bearing = self.plane_bearing
            return self.plane_location

        # Loop through the points and add the distances up to determine where the turn should start
        distance_sum = 0
        path_index = 0
        next_point = None
        current_point = None
        while distance_sum < self.minimum_distance_to_start:
            current_point = self.existing_path[path_index]
            next_point = self.existing_path[path_index + 1]

            distance_between_points = calculate_distance_between_points(current_point, next_point)
            distance_sum += distance_between_points

        # Find out how far from the current point the start can be
        distance_required = distance_sum - self.minimum_distance_to_start

        # Create a point that distance away
        self.start_bearing = math.atan2(next_point.lat - current_point.lat, next_point.lon - current_point.lon)
        return create_point(current_point, distance_required, self.start_bearing)

    def turn_points_generate_points_to_target_radius(self):
        # Determine turn direction
        point_ahead_of_start = create_point(self.start_point, 1, self.start_bearing)
        turn_direction = intersection_orientation(self.target_location, self.start_point, point_ahead_of_start)

        if turn_direction == 1:
            turn_direction = "clockwise"
        elif turn_direction == 2:
            turn_direction = "counterclockwise"
        else:
            print("Collinear oops")
            return None

        # Calculate initial turn circle centre
        self.target_rotation_direction = turn_direction

        if turn_direction == "clockwise":
            centre_point = create_point(self.start_point, self.turn_radius, self.start_bearing - pi / 2)
        else:
            centre_point = create_point(self.start_point, self.turn_radius, self.start_bearing + pi / 2)
        # Find tangency angle between both the target circle and initial turning circle
        exit_angle, entrance_angle = get_tangency_angle(start_centre=centre_point, end_centre=self.target_location, start_radius=self.turn_radius, end_radius=self.target_circle_radius, turn_direction=turn_direction)

        # Create exit point for initial turn and entrance point for target circle
        exit_point = create_point(centre_point, self.turn_radius, exit_angle)
        entrance_point = create_point(self.target_location, self.target_circle_radius, entrance_angle)

        # Get the interpolated turn points
        interpolated_turn_points = general_curve_interpolation(start_point=self.start_point, end_point=exit_point, centre_point=centre_point, radius=self.turn_radius, turn_direction=turn_direction, curve_resolution=self.curve_resolution)

        # Assign the target circle entrance point
        self.target_circle_start_point = entrance_point

        # Return all the points including the entrance point of the target circle
        return interpolated_turn_points


def calculate_distance_between_points(point_1=None, point_2=None):
    return math.sqrt((point_1.lon - point_2.lon) ** 2 + (point_1.lat - point_2.lat) ** 2)

def create_point(point=None, dist=None, angle=None):
    return Coord(lon=point.lon + dist * math.cos(angle), lat=point.lat + dist * math.sin(angle))

def intersection_orientation(p, q, r):
    # To find the orientation of an ordered triplet (p,q,r)

    val = round(((q.lat - p.lat) * (r.lon - q.lon)) - ((q.lon - p.lon) * (r.lat - q.lat)), 10)
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0

def get_tangency_angle(start_centre=None, end_centre=None, start_radius=None, end_radius=None, turn_direction=None):
    radius_current = start_radius
    radius_next = end_radius
    distance = calculate_distance_between_points(start_centre, end_centre)
    reference_angle = math.atan2(end_centre.lat - start_centre.lat, end_centre.lon - start_centre.lon)

    beta = math.acos((radius_current - radius_next) / distance)

    if turn_direction == "clockwise":
        angle_exit = reference_angle + beta
        return angle_exit, angle_exit
    else:
        angle_exit = reference_angle - beta
        return angle_exit, angle_exit


def general_curve_interpolation(start_point=None, start_angle=None, end_point=None, end_angle=None, centre_point=None, radius=None, number_of_turns=None, turn_direction=None, curve_resolution=None):
    if start_point is not None:
        start_angle = calculate_angle_from_points(from_point=centre_point, to_point=start_point)

    if end_point is not None:
        end_angle = calculate_angle_from_points(from_point=centre_point, to_point=end_point)

    # Find inbetween angle based on turn direction
    if turn_direction == "clockwise":
        angle_difference = start_angle - end_angle
    else:
        angle_difference = end_angle - start_angle

    if angle_difference < 0.0:
        angle_difference += 2 * pi

    # Calculate number of points and the angle step
    number_of_points, angle_step = calculate_angle_step_for_curve_interpolation(curve_resolution, radius, angle_difference)

    # If clockwise, make angle step negative
    if turn_direction == "clockwise":
        angle_step = - angle_step

    # Create a bunch of points for the curve
    curve_points = []
    for index in range(number_of_points):
        current_angle = start_angle + index * angle_step
        new_point = create_point(centre_point, radius, current_angle)
        curve_points.append(new_point)

    return curve_points

def calculate_angle_step_for_curve_interpolation(curve_resolution=None, radius=None, angle_difference=None):
    # Find arc length
    arc_length = angle_difference * radius

    # Find how many points will be along the arc must start and end at entrance and exit
    number_of_points = int(1 + math.ceil(arc_length * curve_resolution))

    # Find angle step to achieve these points
    angle_step = angle_difference / number_of_points
    return number_of_points, angle_step

def calculate_angle_from_points(from_point=None, to_point=None):
    y = to_point.lat - from_point.lat
    x = to_point.lon - from_point.lon
    return math.atan2(y, x)

def general_curve_interpolation_v2(start_point=None, start_angle=None, centre_point=None, turn_direction=None, number_of_turns=None, radius=None, curve_resolution=None):
    if start_point is not None:
        start_angle = math.atan2(start_point.lat - centre_point.lat, start_point.lon - centre_point.lon)

    angle_to_complete = number_of_turns * pi * 2
    number_of_points, angle_step = calculate_angle_step_for_curve_interpolation(curve_resolution=curve_resolution, radius=radius, angle_difference=angle_to_complete)

    # If clockwise, make angle step negative
    if turn_direction == "clockwise":
        angle_step = - angle_step

    # Create a bunch of points for the curve
    curve_points = []
    for index in range(number_of_points):
        current_angle = start_angle + index * angle_step
        new_point = create_point(centre_point, radius, current_angle)
        curve_points.append(new_point)

    return curve_points

def plot_waypoints(points_dict=None, points_path=None, point1=None):
    plt.figure(dpi=400)  # Resolution for zoomin in

    if points_dict is not None:
        x_vals = []
        y_vals = []

        for point in points_dict:
            x_vals.append(point["lon"])
            y_vals.append(point["lat"])

        plt.plot(x_vals, y_vals)
        plt.scatter(x_vals, y_vals, color='red', s=5)

    if points_path is not None:
        x_vals = []
        y_vals = []

        for point in points_path:
            x_vals.append(point["lon"])
            y_vals.append(point["lat"])

        plt.plot(x_vals, y_vals)

    plt.scatter(point1.lon, point1.lat, color='purple', s=19)

    plt.axis('equal')
    plt.show()

def main_function():
    path_generator = PathGenerator()

    path_generator.take_off_point = Coord(lat=-38.40, lon=144.88)  # Optional
    path_generator.path_generation_type = PathGenerationType.SEARCH_AREA
    path_generator.minimum_turn_radius = 280  # Metres
    path_generator.curve_resolution = 0.015  # 0.015 waypoints per metre on curves or 1 / 0.015 metres between each waypoint
    path_generator.search_area = Polygon([Coord(-38.383944, 144.880181), Coord(-38.397322, 144.908826), Coord(-38.366840, 144.907242), Coord(-38.364585, 144.880813)])  # Polygon Class that contains list of Coord classes with lat and lon values
    path_generator.paint_overlap = 0.1  # Fraction you want the viewing radius to overlap as the plane flies'
    path_generator.sensor_size = (12.8, 9.6)  # Size of the camera sensor in mm. Optional
    path_generator.focal_length = 16  # Focal length of the camera in mm. Use if sensor size is not None
    path_generator.layer_distance = 400  # Fixed distance between layers of the search path. Optional
    path_generator.orientation = math.pi  # Fixed axis of orientation for the search path. Optional

    # Optional parameters
    path_generator.do_plot = True  # If you want to plot the output

    # Call generate path and collect path points
    path_points = path_generator.generate_path()

    # Fill in parameters
    fly_to_target = FlyToCircleTarget()
    fly_to_target.set_existing_waypoints(path_points)
    fly_to_target.set_parameters(plane_location=path_generator.take_off_point,
                                 plane_bearing=-pi,
                                 target_location=Coord(lat=-38.37, lon=144.88),
                                 turn_radius=280,
                                 target_circle_radius=900,
                                 minimum_distance_to_start=20,
                                 times_to_circle=0.85,
                                 curve_resolution=0.015)

    path = fly_to_target.generate_path()
    print(path)

    plot_waypoints(points_dict=path, points_path=path_points, point1=fly_to_target.target_location)

    # self.plane_location = None  # Coord of plane
    # self.target_location = None  # Coord of target
    # self.turn_radius = None  # Turn radius of the plane
    # self.target_circle_radius = None  # Radius to circle the target at
    # self.minimum_distance_to_start = None  # Minimum distance along the existing before the plane starts turning
    # self.times_to_circle = None  # Number of times to circle the target
    # self.curve_resolution = None  # The number of waypoints per metre


if __name__ == "__main__":
    main_function()