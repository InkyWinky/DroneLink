from __future__ import division, print_function
import matplotlib.pyplot as plt
import math

pi = 3.141592653589793

class Polygon:
    def __init__(self, vertices=None):
        self.vertices = vertices  # List of Point instances

class Waypoint:
    def __init__(self, x=None, y=None):
        self.coords = Point(x, y)  # Point instance that stores location of waypoint
        self.centre_point = None  # Point instance
        self.entrance = None  # Point instance for where the Albatross starts turning
        self.exit = None  # Point instance for where the Albatross stops turning
        self.desired_entrance_direction = None  # Direction in radians that the Albatross is facing when it starts turning
        self.desired_exit_direction = None  # Direction in radians that the Albatross is facing when it stops turning
        self.turn_direction = None  # "clockwise" or "counter_clockwise"
        self.curve_waypoints = None  # List of Point instances that are the interpolated points of the curve

class Point:
    def __init__(self, x=None, y=None):
        self.x = x  # Longitude
        self.y = y  # Latitude

    def magnitude(self, point=None):
        if point is None:
            return math.sqrt(self.x ** 2 + self.y ** 2)
        else:
            return math.sqrt(point.x ** 2 + point.y ** 2)

    def dot(self, point_2):
        return self.x * point_2.x + self.y * point_2.y


def calculate_distance_between_points(point_1=None, point_2=None):
    return math.sqrt((point_1.x - point_2.x) ** 2 + (point_1.y - point_2.y) ** 2)


class SearchPathGenerator:
    def __init__(self):
        pass

    # Input Data (points and boundaries)
    raw_waypoints = None  # List of rough waypoints to travel through
    search_area = None  # Polygon class instance that defines the boundary of the search area the plane will scan
    boundary = None  # Polygon class instance that defines the boundary that the path must remain in. Path can be on the boundary
    start_point = None  # Point where the Albatross takes off
    end_point = None  # Point where the Albatross should land

    # Input Parameters
    orientation_resolution = None  # An inversely proportional factor to the step size the axis of orientation will be calculated at
    minimum_turning_radius = None  # The minimum turning radius of the plane at cruise speed in metres
    boundary_resolution = None  # A factor inversely proportional to the step size that the path will adjust to avoid the boundary
    boundary_tolerance = None  # The minimum distance from the boundary the path must remain
    orientation_input = None  # Optional desired axis of orientation set by the user
    curve_resolution = None  # How many waypoints per metre we want
    max_flight_time = None  # The maximum amount of flight time
    paint_overlap = None  # Minimum paint overlap required in terms of percentage. Must be less than 100%
    paint_radius = None  # The radius in metres around the plane that the cameras can see / paint

    # Output Data
    orientation_output = None  # Main axis of orientation of flight path
    path_waypoints = None  # Generated list of Waypoint class instances that make up the search path
    flight_time = None  # Calculated (estimate) flight time for the given path

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
        axis_of_orientation = self.calculate_axis_of_orientation_method_2()

        # Find the first coordinate of the grid search. This will depend on the take-off position of the Albatross

        # Calculate points that once connected, will "search" the entire grid along with desired overlap percentage

        # Update the self.waypoints will the search grid waypoints

        # Okay so here I'm doing a run where the best orientation has already been found, or that the user has input a specific angle
        # 1. Find the closest point

    def calculate_axis_of_orientation_method_1(self):
        # Loop through all orientation steps
        axis_of_orientation = 0
        while axis_of_orientation < 2 * pi:
            # Do calculation with current axis of orientation
            pass
            # Calculate number of turns and

    def calculate_axis_of_orientation_method_2(self):
        # Start point is a point that is reached when the Albatross flies from the start location to the closest search area segment then a little further, paint radius
        # Find the closest point of the search area boundary from the start location
        search_area_closest_point = self.calculate_closest_search_area_boundary_point()
        overlap_radius = self.paint_radius * (1 - self.paint_overlap)
        direction_from_start = Point(search_area_closest_point.x - self.start_point.x, search_area_closest_point.y - self.start_point.y)
        magnitude = math.sqrt(direction_from_start.x + direction_from_start.y)
        unit_direction = Point(direction_from_start.x / magnitude, direction_from_start.y / magnitude)
        amount_to_add = Point(unit_direction.x * overlap_radius, unit_direction.y * overlap_radius)
        starting_point = Point(search_area_closest_point.x + amount_to_add.x, search_area_closest_point.y + amount_to_add.y)
        # Figure out how many turns there will be given the starting location, search area, axis of orientation, paint radius, paint overlap
        number_of_turns, est_flight_time = self.calculate_turns_and_flight_time(starting_point)

    def calculate_turns_and_flight_time(self, starting_point):
        minimum_raycast = self.paint_radius * (1 - self.paint_overlap)
        calculated_points = [starting_point]
        # Go in the direction of axis of orientation and map out the potential points
        number_of_blocks = 0
        direction = "forward"
        while number_of_blocks < 2:
            raycast_point = self.raycast_to_polygon(calculated_points[-1], self.orientation_input, self.search_area)
            reverse_raycast = Point(calculated_points[-1].x - raycast_point.x, calculated_points[-1].y - raycast_point.y)
            magnitude = math.sqrt(reverse_raycast.x ** 2 + reverse_raycast.y ** 2)
            unit_reverse_raycast = Point(reverse_raycast.x / magnitude, reverse_raycast.y / magnitude)
            adjusted_raycast_point = Point(raycast_point.x + unit_reverse_raycast.x * minimum_raycast, raycast_point.y + unit_reverse_raycast.y * minimum_raycast)
            # Check if point is backwards after adjusting
            if adjusted_raycast_point.dot(calculated_points[-1]) <= 0:
                number_of_blocks += 1
                if direction == "forward":
                    direction = "left"
                if direction == "forward left":
                    direction = "backward"
                if direction == "backward left":
                    direction = "forward"
                if direction == "backward":
                    direction = "left"
            else:
                number_of_blocks = 0
                calculated_points.append(adjusted_raycast_point)

        # Go in reverse direction of axis of orientation and map out the rest of the point


    def raycast_to_polygon(self, origin=None, direction=None, polygon=None, max_dist=None):
        """
        Perform a raycast from an origin point until it collides with a polygon. If it does, return the point it collides with.
        Will cast for max_dist if specified.
        :param origin: Point the raycast starts at
        :param polygon: Polygon to check if the ray hits it
        :param max_dist: Maximum distance to cast the ray. This is optional
        :return: Returns a point where the raycast hits the polygon or None if nothing was hit after max_dist.
        """
        pass

    def calculate_closest_search_area_boundary_point(self):
        # Loop over each segment of search area
        closest_point = None
        closest_distance = None
        for index in range(len(self.search_area.vertices)):
            segment_point_1 = self.search_area.vertices[index]
            segment_point_2 = self.search_area.vertices[(index + 1) % len(self.search_area.vertices)]
            # Find the closest point on segment to start location
            new_closest_point = calculate_closest_point_on_segment_to_point(segment_point_1, segment_point_2, self.start_point)
            new_closest_distance = calculate_distance_between_points(closest_point, self.start_point)
            if closest_point is None or new_closest_distance < closest_distance:
                closest_point = new_closest_point
                closest_distance = new_closest_distance
        return closest_point

    def do_validation_checks(self):
        # Ensure the class instance has all the data and parameters it needs to generate a path
        validation_flag, error_message = self.validation_data_parameters()
        if validation_flag is None:
            return validation_flag, error_message

        # Ensure the user has decided whether to do search area or raw waypoints
        validation_flag, error_message = self.validation_operation_choice()
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
        if self.minimum_turning_radius is None or self.curve_resolution is None:
            return None, "Not all essential data or parameters are set in the class instance"

    def validation_operation_choice(self):
        if not (self.raw_waypoints is None and self.search_area is not None) or (self.raw_waypoints is not None and self.search_area is None):
            return None, "Choose either search area calculation or raw waypoint calculation, not both or none"

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


"""
Functions. Mostly just math functions.
"""

def calculate_closest_point_on_segment_to_point(segment_start=None, segment_end=None, reference_point=None):
    segment_vector = Point(segment_end.x - segment_start.x, segment_end.y - segment_start.y)
    segment_to_reference = Point(reference_point.x - segment_start.x, reference_point.y - segment_start.y)
    percentage_along_segment = (segment_to_reference.x * segment_vector.x + segment_to_reference.y * segment_vector.y) / (segment_vector.x ** 2 + segment_vector.y ** 2)
    percentage_along_segment = max(0, min(percentage_along_segment, 1))
    closest_point = Point(segment_start.x + percentage_along_segment * segment_vector.x, segment_start.y + percentage_along_segment * segment_vector.y)
    return closest_point

def main_function(self):
    raw_waypoints = [[0, 0], [2, 4], [5, 2], [3, -2], [6, -2], [3, -5], [1, -4]]
    minimum_turn_radius = 0.5
    search_area = [[0, 0], [0, 10], [10, 10], [10, 0]]
    curve_resolution = 4

    search_area_polygon = []
    for point in search_area:
        search_area_polygon.append(Point(point[0], point[1]))
    search_area_polygon = Polygon(search_area_polygon)

    path_generator = SearchPathGenerator()
    path_generator.set_data(search_area=search_area_polygon)
    path_generator.set_parameters(minimum_turn_radius=minimum_turn_radius, curve_resolution=curve_resolution)

    path_generator.generate_path()


if __name__ == "__main__":
    main_function()