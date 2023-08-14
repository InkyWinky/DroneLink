from __future__ import division, print_function

import time
# Test
import matplotlib.pyplot as plt
import math
import random

pi = 3.141592653589793
random.seed(time.time())

class Polygon:
    def __init__(self, vertices=None):
        self.vertices = vertices  # List of Point instances
        self.maximum = self.calculate_maximum_length()
        self.segments = self.calculate_segments()
        self.count = self.calculate_count()
        self.centroid = self.calculate_centroid()

    def calculate_centroid(self):
        x_sum = 0
        y_sum = 0
        for vertex in self.vertices:
            x_sum += vertex.x
            y_sum += vertex.y
        x_avg = x_sum / self.count
        y_avg = y_sum / self.count
        centroid = Point(x_avg, y_avg)
        return centroid

    def calculate_maximum_length(self):
        max_length = 0
        for vertex1_index in range(len(self.vertices)):
            for vertex2_index in range(len(self.vertices) - 1):
                if vertex1_index == vertex2_index:
                    continue
                vertex1 = self.vertices[vertex1_index]
                vertex2 = self.vertices[vertex2_index]
                length = calculate_distance_between_points(vertex1, vertex2)
                if length > max_length:
                    max_length = length
        return max_length

    def calculate_segments(self):
        segments = []
        for index in range(len(self.vertices)):
            vertex1 = self.vertices[index]
            vertex2 = self.vertices[(index + 1) % len(self.vertices)]
            new_segment = Segment(vertex1, vertex2)
            segments.append(new_segment)
        return segments

    def calculate_count(self):
        count = len(self.vertices)
        return count

    def contains(self, point=None):
        # Cast ray to the right and count how many intersections
        ray_end = create_point(point, self.maximum, 0)
        ray = Segment(point, ray_end)
        intersection_count = 0
        intersections = []
        for segment in self.segments:
            if do_segments_intersect(ray, segment):
                intersection_count += 1
                intersections.append(find_segment_intersection(ray, segment))

        # If no intersections, point not in the polygon
        if intersection_count == 0:
            return False

        # Filter out duplicate points
        indices_to_remove = []
        for index1, point1 in enumerate(intersections):
            for index2, point2 in enumerate(intersections):
                if index1 != index2 and point1.equals(point2):
                    indices_to_remove.append(index1)

        indices_to_remove.sort()
        for index in indices_to_remove:
            intersections.pop(index)

        # If odd intersection count, point is contained by polygon
        if intersection_count % 2 != 0:
            return True

        # If even intersection count, point is not with polygon
        return False


class Waypoint:
    def __init__(self, x=None, y=None):
        self.coords = Point(x, y)  # Point instance that stores location of waypoint
        self.centre_point = None  # Point instance
        self.turn_type = None  # "circle", "double circle" "lightbulb", "lightbulb angled"
        self.entrance = None  # Point instance for where the Albatross starts turning
        self.exit = None  # Point instance for where the Albatross stops turning
        self.turn_direction = None  # "clockwise" or "counterclockwise"
        self.curve_waypoints = None  # List of Point instances that are the interpolated points of the curve
        self.lightbulb_pairs = None  # List of 3 pairs of entrances and exits for a lightbulb turn


class Segment:
    def __init__(self, start_point=None, end_point=None):
        self.start = start_point
        self.end = end_point

    def length(self):
        return calculate_distance_between_points(self.start, self.end)


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

    def multiply(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def equals(self, point=None):
        if self.x == point.x and self.y == point.y:
            return True
        return False


class SearchPathGenerator:
    def __init__(self):
        pass

    # Input Data (points and boundaries)
    raw_waypoints = None  # List of rough waypoints to travel through
    search_area = None  # Polygon class instance that defines the boundary of the search area the plane will scan
    boundary = None  # Polygon class instance that defines the boundary that the path must remain in. Path can be on the boundary
    take_off_point = None  # Point where the Albatross takes off
    landing_point = None  # Point where the Albatross should land

    # Input Parameters
    turn_radius = None  # The minimum turning radius of the plane at cruise speed in metres
    boundary_resolution = None  # A factor inversely proportional to the step size that the path will adjust to avoid the boundary
    boundary_tolerance = None  # The minimum distance from the boundary the path must remain
    orientation = None  # Desired axis of orientation set by the user or calculated as the most efficient
    curve_resolution = None  # How many waypoints per metre we want
    max_flight_time = None  # The maximum amount of flight time
    sensor_size = None  # (width, height) in mm
    focal_length = None  # Lens focal length in mm
    paint_overlap = None  # Minimum paint overlap required in terms of percentage. Must be less than 100%
    paint_radius = None  # The radius in metres around the plane that the cameras can see / paint
    perimeter_distance = None  # The distance rough points will be placed from the search area perimeter
    layer_distance = None  # Distance between each 'layer' of the flight path
    turn_type = None  # Turn type for the turns in search area mode
    search_area_coverage = None  # Coverage of search area in fraction that the plane can see if following the current path points

    error = False  # Flag for if an error occurred during runtime

    # Output Data
    path_waypoints = None  # Generated list of Waypoint class instances that make up the search path
    flight_time = None  # Calculated (estimate) flight time for the given path

    # Callable Data
    path_points = None  # Points in x and y format that make the entire path

    def set_search_area(self, waypoints):
        """
        Takes in a list of dictionaries containing "long", "lat", and "alt" keys.
        """
        points = []
        for waypoint in waypoints:
            new_point = Point(waypoint["long"], waypoint["lat"])
            points.append(new_point)

        search_area = Polygon(points)
        self.search_area = search_area

    def get_waypoints(self):
        """
        Call this function to get a dictionary of every point in the path. The format is as follows:
        [{"long": 101.24, "lat": 62.76, "alt": 100}, {"long": 98.64, "lat": 65.22, "alt": 100}, ...]
        """
        dict_list = []

        for point in self.path_points:
            new_dict_entry = {"long": point.x, "lat": point.y, "alt": 100}
            dict_list.append(new_dict_entry)

        return dict_list

    def set_data(self, raw_waypoints=None, search_area=None, boundary=None):
        if raw_waypoints is not None:
            self.raw_waypoints = raw_waypoints
        if search_area is not None:
            self.search_area = search_area
        if boundary is not None:
            self.boundary = boundary

    def set_parameters(self, minimum_turn_radius=None, boundary_resolution=None, layer_distance=None, boundary_tolerance=None, curve_resolution=None, orientation=None, start_point=None, focal_length=None, sensor_size=None, paint_overlap=None):
        if minimum_turn_radius is not None:
            self.turn_radius = minimum_turn_radius
        if boundary_resolution is not None:
            self.boundary_resolution = boundary_resolution
        if boundary_tolerance is not None:
            self.boundary_tolerance = boundary_tolerance
        if curve_resolution is not None:
            self.curve_resolution = curve_resolution
        if orientation is not None:
            self.orientation = orientation
        if start_point is not None:
            self.take_off_point = start_point
        if focal_length is not None:
            self.focal_length = focal_length
        if sensor_size is not None:
            self.sensor_size = sensor_size
        if paint_overlap is not None:
            self.paint_overlap = paint_overlap
        if layer_distance is not None:
            self.layer_distance = layer_distance

    def generate_path(self, do_plot=True):
        # Pre-algorithm calculations
        if self.sensor_size is not None and self.focal_length is not None and self.layer_distance is None:
            self.paint_radius = calculate_viewing_radius(sensor_size=self.sensor_size, focal_length=self.focal_length, altitude=100)
            self.layer_distance = calculate_layer_distance(viewing_radius=self.paint_radius, paint_overlap=self.paint_overlap)
        if self.orientation is None:
            self.orientation = calculate_best_orientation(polygon=self.search_area)

        # Complete pre-calculation data and parameter validation checks
        validation, error_message = self.do_pre_validation_checks()
        if validation is None:
            print(error_message)
            self.error = True
            return validation, error_message

        # Generate path points
        rough_points = self.generate_points()
        self.smooth_rough_points(rough_points=rough_points)

        # Calculate callable point
        self.path_points = self.calculate_path_points()

        # Complete post-calculation data validation checks
        if rough_points is not None:
            validation, error_message = self.do_post_validation_checks(waypoints=rough_points)
        if do_plot:
            # print_waypoints(rough_points)
            self.plot_waypoints(waypoints=rough_points, polygon=self.search_area, actual_waypoints=self.path_waypoints)
            self.plot_points(points=self.path_points, polygon=self.search_area, actual_waypoints=self.path_waypoints)
            print("Breakpoint")
        elif validation is None:
            self.error = error_message
            self.print_debug()
            self.plot_waypoints(waypoints=rough_points, polygon=self.search_area, actual_waypoints=self.path_waypoints)

    def plot_points(self, points=None, polygon=None, actual_waypoints=None):
        # Plot all points
        x_vals = [point.x for point in points]
        y_vals = [point.y for point in points]
        plt.plot(x_vals, y_vals, color='red')
        plt.scatter(x_vals, y_vals, color='b', s=13)

        # Plot original waypoints if given
        if actual_waypoints is not None:
            x_original = [point.coords.x for point in actual_waypoints]
            y_original = [point.coords.y for point in actual_waypoints]
            plt.scatter(x_original, y_original, color='black')

        # Plot polygon if given
        if polygon is not None:
            x_polygon = [point.x for point in polygon.vertices]
            x_polygon.append(polygon.vertices[0].x)
            y_polygon = [point.y for point in polygon.vertices]
            y_polygon.append(polygon.vertices[0].y)
            plt.plot(x_polygon, y_polygon, color='black')

        if self.take_off_point is not None:
            plt.scatter(self.take_off_point.x, self.take_off_point.y, marker='^', color='black')
            plt.annotate("Takeoff", (self.take_off_point.x, self.take_off_point.y), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.annotate("First Waypoint", (self.path_points[0].x, self.path_points[0].y), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.annotate("Final Waypoint", (self.path_points[-1].x, self.path_points[-1].y), textcoords="offset points", xytext=(0, 10), ha='center')

        # Plot it all
        plt.axis('equal')
        plt.show()

    def calculate_path_points(self):
        if self.path_waypoints is None:
            return None
        points = [self.path_waypoints[0].coords]

        for waypoint in self.path_waypoints:
            if waypoint.centre_point is None:
                points.append(waypoint.coords)
                continue

            if waypoint.curve_waypoints is not None:
                if type(waypoint.curve_waypoints[0]) == list:
                    # Lightbulb turn
                    for turn in waypoint.curve_waypoints:
                        for point in turn:
                            points.append(point)
                else:
                    for point in waypoint.curve_waypoints:
                        points.append(point)

        return points

    def print_debug(self):
        print("ERROR:", self.error)
        print("\tSearch Area:")
        for vertex in self.search_area.vertices:
            print("\t\t", vertex.x, vertex.y)
        print("\tStart Point:")
        print("\t\t", self.take_off_point.x, self.take_off_point.y)
        print("\tLayer Distance:")
        print("\t\t", self.layer_distance)

    def smooth_rough_points(self, rough_points=None):
        if rough_points is None:
            return None
        # Create waypoints out of each point
        self.path_waypoints = create_waypoints_from_points(points=rough_points)
        if len(self.path_waypoints) <= 1:
            print("There is only one waypoint")
            return None
        self.calculate_turn_directions()
        self.calculate_turn_type()
        self.create_turn_points()
        self.interpolate_all_turns()

    def create_turn_points(self):
        if on_same_axis(self.path_waypoints[0].coords, self.path_waypoints[1].coords, self.orientation):
            start_offset = 1
        else:
            start_offset = 0

        if on_same_axis(self.path_waypoints[-1].coords, self.path_waypoints[-2].coords, self.orientation):
            end_offset = 1
        else:
            end_offset = 0

        for index in range(start_offset, len(self.path_waypoints) - 1 - end_offset, 2):
            self.path_waypoints[index].centre_point, self.path_waypoints[index + 1].centre_point = create_centre_points(current_waypoint=self.path_waypoints[index].coords,
                                                                                                                        next_waypoint=self.path_waypoints[index + 1].coords,
                                                                                                                        orientation=self.orientation,
                                                                                                                        turn_radius=self.turn_radius,
                                                                                                                        turn_type=self.turn_type,
                                                                                                                        direction=self.path_waypoints[index].turn_direction,
                                                                                                                        layer_distance=self.layer_distance)
            self.path_waypoints[index].entrance, \
            self.path_waypoints[index].exit, \
            self.path_waypoints[index + 1].entrance, \
            self.path_waypoints[index + 1].exit = calculate_entrance_and_exit(current_waypoint=self.path_waypoints[index].coords,
                                                                              current_waypoint_centre_point=self.path_waypoints[index].centre_point,
                                                                              next_waypoint=self.path_waypoints[index + 1].coords,
                                                                              next_waypoint_centre_point=self.path_waypoints[index + 1].centre_point,
                                                                              turn_radius=self.turn_radius,
                                                                              direction=self.path_waypoints[index].turn_direction,
                                                                              orientation=self.orientation,
                                                                              turn_type=self.turn_type)

            # If a lightbulb turn move the data
            if type(self.path_waypoints[index].entrance) == list:
                self.path_waypoints[index].lightbulb_pairs = self.path_waypoints[index].entrance
                self.path_waypoints[index].entrance = None

        # If first waypoint is a double circle turn, remove the entrance, exit, and centre point
        if self.path_waypoints[0].centre_point is not None and self.turn_type == "double circle":
            self.path_waypoints[0].centre_point = None
            self.path_waypoints[0].entrance = None
            self.path_waypoints[0].exit = None

    def calculate_turn_directions(self):
        for index in range(1, len(self.path_waypoints) - 1):
            direction = intersection_orientation(self.path_waypoints[index - 1].coords, self.path_waypoints[index].coords, self.path_waypoints[index + 1].coords)
            if direction == 1:
                direction = "clockwise"
            elif direction == 2:
                direction = "counterclockwise"
            else:
                direction = "collinear"
            self.path_waypoints[index].turn_direction = direction

        # Check first point
        if not on_same_axis(self.path_waypoints[0].coords, self.path_waypoints[1].coords, self.orientation):
            self.path_waypoints[0].turn_direction = self.path_waypoints[1].turn_direction

        # Check last point
        if not on_same_axis(self.path_waypoints[-1].coords, self.path_waypoints[-2].coords, self.orientation):
            self.path_waypoints[-1].turn_direction = self.path_waypoints[-2].turn_direction

    def calculate_turn_type(self):
        if 2 * self.turn_radius < self.layer_distance:
            if 4 * self.turn_radius < self.layer_distance:
                self.turn_type = "double circle"
            else:
                self.turn_type = "circle"
        else:
            self.turn_type = "lightbulb"

    def interpolate_all_turns(self):
        for waypoint in self.path_waypoints:
            if waypoint.centre_point is not None:
                # Interpolate the curve to curve resolution
                if self.turn_type == "double circle" or self.turn_type == "circle":
                    waypoint.curve_waypoints = calculate_curve_waypoints_for_double_circle_or_circle(waypoint=waypoint, curve_resolution=self.curve_resolution, radius=self.turn_radius, turn_type=self.turn_type)
                elif self.turn_type == "lightbulb":
                    waypoint.curve_waypoints = calculate_curve_waypoints_for_lightbulb(waypoint=waypoint, curve_resolution=self.curve_resolution, radius=self.turn_radius)

    def evaluate_coverage(self):
        # This function evaluates how much of the search area the plane will see based on factors such as layer distance
        return None

    def plot_waypoints(self, waypoints=None, polygon=None, equal_axis=True, centre_points=None, actual_waypoints=None):
        poly_x = []
        poly_y = []
        for point in polygon.vertices:
            poly_x.append(point.x)
            poly_y.append(point.y)
        poly_x.append(polygon.vertices[0].x)
        poly_y.append(polygon.vertices[0].y)
        plt.plot(poly_x, poly_y, color='black')

        x_vals = []
        y_vals = []
        for point in waypoints:
            x_vals.append(point.x)
            y_vals.append(point.y)
        plt.plot(x_vals, y_vals, color='blue')
        plt.scatter(x_vals, y_vals, color='blue')

        x_centre = []
        y_centre = []
        for waypoint in actual_waypoints:
            if waypoint.centre_point is not None:
                if type(waypoint.centre_point) == list:
                    for point in waypoint.centre_point:
                        x_centre.append(point.x)
                        y_centre.append(point.y)
                else:
                    x_centre.append(waypoint.centre_point.x)
                    y_centre.append(waypoint.centre_point.y)
        if len(x_centre) > 0:
            plt.scatter(x_centre, y_centre, color='orange')

        x_entrance = []
        y_entrance = []
        x_exit = []
        y_exit = []
        for waypoint in actual_waypoints:
            if waypoint.entrance is not None:
                x_entrance.append(waypoint.entrance.x)
                y_entrance.append(waypoint.entrance.y)
                x_exit.append(waypoint.exit.x)
                y_exit.append(waypoint.exit.y)
            if waypoint.lightbulb_pairs is not None:
                for pair in waypoint.lightbulb_pairs:
                    x_entrance.append(pair[0].x)
                    y_entrance.append(pair[0].y)
                    x_exit.append(pair[1].x)
                    y_exit.append(pair[1].y)
        if len(x_entrance) > 0:
            plt.scatter(x_entrance, y_entrance, color='green')
            plt.scatter(x_exit, y_exit, color='green')


        plt.scatter(waypoints[0].x, waypoints[0].y, color='red')
        plt.annotate("First waypoint", (waypoints[0].x, waypoints[0].y), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.scatter(self.search_area.centroid.x, self.search_area.centroid.y, color='purple')
        plt.annotate("Centre of calculations", (self.search_area.centroid.x, self.search_area.centroid.y), textcoords="offset points", xytext=(0, 10), ha='center')
        if self.take_off_point is not None:
            plt.scatter(self.take_off_point.x, self.take_off_point.y, marker='^', color='black')
            plt.annotate("Takeoff", (self.take_off_point.x, self.take_off_point.y), textcoords="offset points", xytext=(0, 10), ha='center')

        if equal_axis:
            plt.axis('equal')

        plt.title(self.orientation * 180 / pi)
        plt.xlabel(self.layer_distance)
        plt.show()

    def do_post_validation_checks(self, waypoints=None):
        # Check if any points lie outside the polygon
        validation_flag, error_message = self.validation_point_outside_polygon(waypoints)
        if validation_flag is None:
            return validation_flag, error_message

        # Check if any path segments overlap with each other
        validation_flag, error_message = self.validation_path_segment_overlap(waypoints)
        if validation_flag is None:
            return validation_flag, error_message

        return "All g", "All g"

    def validation_point_outside_polygon(self, waypoints):
        for point in waypoints:
            if not self.search_area.contains(point) and len(waypoints) > 1:
                return None, "A point is not in the search area"
        return "All g", "All g"

    def validation_path_segment_overlap(self, waypoints):
        # This function was fixed by rounding the val in the orientation calculation for do segments intersecting. This is to avoid floating point error
        for index1 in range(len(waypoints) - 3):
            vertex1 = waypoints[index1]
            vertex2 = waypoints[index1 + 1]
            edge1 = Segment(vertex1, vertex2)
            for index2 in range(index1 + 2, len(waypoints) - 1):
                vertex3 = waypoints[index2]
                vertex4 = waypoints[index2 + 1]
                edge2 = Segment(vertex3, vertex4)

                # Check for collision
                if do_segments_intersect(edge1, edge2):
                    print("INTERSECTION:", edge1.start.x, edge1.start.y)
                    print("INTERSECTION:", edge1.end.x, edge1.end.y)
                    print("INTERSECTION:", edge2.start.x, edge2.start.y)
                    print("INTERSECTION:", edge2.end.x, edge2.end.y)
                    return None, "Two path segments intersect"

        return "All g", "All g"

    def generate_points(self):
        # Generate the first point depending on where the plane starts
        centroid = self.search_area.centroid
        forwards_waypoints = calculate_points_along_polygon_distanced(start_point=centroid, polygon=self.search_area, orientation=self.orientation, layer_distance=self.layer_distance, direction="forward")
        forwards_waypoints.pop(0)  # Remove the path start point
        backwards_waypoints = calculate_points_along_polygon_distanced(start_point=centroid, polygon=self.search_area, orientation=self.orientation + pi, layer_distance=self.layer_distance, direction="backward")
        backwards_waypoints.pop(0)  # Remove the path start point
        backwards_waypoints.reverse()

        rough_waypoints = []
        rough_waypoints.extend(backwards_waypoints)
        rough_waypoints.extend(forwards_waypoints)

        # Check for no solution
        if len(rough_waypoints) < 1:
            return None

        # Find which end of the path is closest to the take-off location. Make the closest one the zeroth index by reversing if necessary
        if self.take_off_point is not None:
            distance_start = calculate_distance_between_points(self.take_off_point, rough_waypoints[0])
            distance_end = calculate_distance_between_points(self.take_off_point, rough_waypoints[-1])
            if distance_end < distance_start:
                rough_waypoints.reverse()

        return rough_waypoints

    def generate_first_point(self):
        # Left of the orientation axis is negative and to the right is positive
        # Check if the start point is in the search area or not
        if not self.search_area.contains(self.take_off_point):
            # Find the closest point along the polygon from the start point
            closest_point = calculate_closest_point_on_polygon(polygon=self.search_area, start_point=self.take_off_point)
        else:
            closest_point = self.take_off_point
        # Find the closest point that is the furthest away from the start point in the perpendicular directions
        closest_vertex, closest_vertex_index = calculate_closest_perpendicular_vertex(polygon=self.search_area, orientation=self.orientation, start_point=closest_point)
        # Move d distance away from walls
        path_start = calculate_point_away_from_polygon(polygon=self.search_area, centre_vertex_index=closest_vertex_index, distance=self.layer_distance)
        return path_start

    def do_pre_validation_checks(self):
        # Ensure the class instance has all the data and parameters it needs to generate a path
        validation_flag, error_message = self.validation_data_parameters()
        if validation_flag is None:
            return validation_flag, error_message

        # Ensure the user has decided whether to do search area or raw waypoints
        validation_flag, error_message = self.validation_operation_choice()
        if validation_flag is None:
            return validation_flag, error_message

        # Check the search area for open ends
        validation_flag, error_message = self.validation_boundary_polygon()
        if validation_flag is None:
            return validation_flag, error_message

        return "All g", "All g"

    def validation_data_parameters(self):
        if self.turn_radius is None or self.curve_resolution is None:
            return None, "Not all essential data or parameters are set in the class instance"
        return "All g", "All g"

    def validation_operation_choice(self):
        if not (self.raw_waypoints is None and self.search_area is not None) or (self.raw_waypoints is not None and self.search_area is None):
            return None, "Choose either search area calculation or raw waypoint calculation, not both or none"
        return "All g", "All g"

    def validation_boundary_polygon(self):
        if self.boundary is not None:
            for index in range(len(self.boundary) - 1):
                if self.boundary[index] != self.boundary[index + 1]:
                    return None, "The boundary polygon is not closed"
        return "All g", "All g"


"""
Functions. Mostly just math functions.
"""

def calculate_curve_waypoints_for_lightbulb(waypoint=None, curve_resolution=None, radius=None):
    if waypoint.turn_direction == "clockwise":
        centre_direction = "clockwise"
        side_direction = "counterclockwise"
    else:
        centre_direction = "counterclockwise"
        side_direction = "clockwise"

    first_turn_points = curve_interpolation(centre_point=waypoint.centre_point[0], entrance_point=waypoint.lightbulb_pairs[0][0], exit_point=waypoint.lightbulb_pairs[0][1], turn_radius=radius, turn_direction=side_direction, curve_resolution=curve_resolution)
    middle_turn_points = curve_interpolation(centre_point=waypoint.centre_point[1], entrance_point=waypoint.lightbulb_pairs[1][0], exit_point=waypoint.lightbulb_pairs[1][1], turn_radius=radius, turn_direction=centre_direction, curve_resolution=curve_resolution)
    third_turn_points = curve_interpolation(centre_point=waypoint.centre_point[2], entrance_point=waypoint.lightbulb_pairs[2][0], exit_point=waypoint.lightbulb_pairs[2][1], turn_radius=radius, turn_direction=side_direction, curve_resolution=curve_resolution)

    return [first_turn_points, middle_turn_points, third_turn_points]

def curve_interpolation(centre_point=None, entrance_point=None, exit_point=None, turn_radius=None, turn_direction=None, curve_resolution=None):
    # Find start angle
    start_angle = calculate_angle_from_points(from_point=centre_point, to_point=entrance_point)

    # Find end angle
    end_angle = calculate_angle_from_points(from_point=centre_point, to_point=exit_point)

    # Find inbetween angle based on turn direction
    if turn_direction == "clockwise":
        angle_difference = start_angle - end_angle
    else:
        angle_difference = end_angle - start_angle

    if angle_difference < 0.0:
        angle_difference += 2 * pi

    # Find angle step
    number_of_points, angle_step = calculate_angle_step_for_curve_interpolation(curve_resolution=curve_resolution, radius=turn_radius, angle_difference=angle_difference)

    # Clockwise or counter-clockwise for angle step
    if turn_direction == "clockwise":
        angle_step = - angle_step

    # Loop through and make the waypoints
    curve_waypoints = []
    for index in range(number_of_points - 1):
        current_angle = start_angle + angle_step * index
        new_point = create_point(centre_point, turn_radius, current_angle)
        curve_waypoints.append(new_point)

    return curve_waypoints

def calculate_curve_waypoints_for_double_circle_or_circle(waypoint=None, curve_resolution=None, radius=None, turn_type=None):
    # Find start angle
    start_angle = calculate_angle_from_points(from_point=waypoint.centre_point, to_point=waypoint.entrance)

    # Find end angle
    end_angle = calculate_angle_from_points(from_point=waypoint.centre_point, to_point=waypoint.exit)

    # Find inbetween angle based on turn direction
    if waypoint.turn_direction == "clockwise":
        angle_difference = start_angle - end_angle
    else:
        angle_difference = end_angle - start_angle

    if angle_difference < 0.0:
        angle_difference += 2 * pi

    # Change radius if needed
    if turn_type == "circle":
        radius = calculate_distance_between_points(waypoint.centre_point, waypoint.entrance)

    # Find angle step
    number_of_points, angle_step = calculate_angle_step_for_curve_interpolation(curve_resolution=curve_resolution, radius=radius, angle_difference=angle_difference)

    # Clockwise or counter-clockwise for angle step
    if waypoint.turn_direction == "clockwise":
        angle_step = - angle_step

    # Loop through and make the waypoints
    curve_waypoints = []
    for index in range(number_of_points):
        current_angle = start_angle + angle_step * index
        new_point = create_point(waypoint.centre_point, radius, current_angle)
        curve_waypoints.append(new_point)

    return curve_waypoints

def calculate_angle_step_for_curve_interpolation(curve_resolution=None, radius=None, angle_difference=None):
    # Find arc length
    arc_length = angle_difference * radius

    # Find how many points will be along the arc must start and end at entrance and exit
    number_of_points = int(1 + math.ceil(arc_length * curve_resolution))

    # Find angle step to achieve these points
    angle_step = angle_difference / number_of_points
    return number_of_points, angle_step

def calculate_angle_from_points(from_point=None, to_point=None):
    y = to_point.y - from_point.y
    x = to_point.x - from_point.x
    return math.atan2(y, x)

def calculate_best_orientation(polygon=None):
    # TODO: Make sure you return the correct orientation (+ or - pi or plus at all)
    best_distance = 0
    best_orientation = 0
    for vertex1 in polygon.vertices:
        for vertex2 in polygon.vertices:
            if vertex1 == vertex2:
                continue
            distance = calculate_distance_between_points(vertex1, vertex2)
            if distance > best_distance:
                best_orientation = calculate_angle_from_points(from_point=vertex1, to_point=vertex2)
                best_distance = distance
    return clamp_angle(best_orientation - pi)

def raycast_to_polygon(origin=None, direction=None, polygon=None):
    # Define the ray as a line
    ray = Segment(origin, Point(origin.x + polygon.maximum * math.cos(direction), origin.y + polygon.maximum * math.sin(direction)))
    # Look over each edge of polygon and check for intersection
    # plt.plot([ray.start.x, ray.end.x], [ray.start.y, ray.end.y], '-.')
    for index in range(len(polygon.vertices)):
        vertex1 = polygon.vertices[index]
        vertex2 = polygon.vertices[(index + 1) % len(polygon.vertices)]

        edge = Segment(vertex1, vertex2)
        if do_segments_intersect(segment1=ray, segment2=edge):
            intersection_point = find_segment_intersection(segment1=ray, segment2=edge)
            return intersection_point

    return None

def onSegment(p, q, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False

def intersection_orientation(p, q, r):
    # To find the orientation of an ordered triplet (p,q,r)

    val = round(((q.y - p.y) * (r.x - q.x)) - ((q.x - p.x) * (r.y - q.y)), 10)
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0

def do_segments_intersect(segment1=None, segment2=None):
    p1, q1 = segment1.start, segment1.end
    p2, q2 = segment2.start, segment2.end

    # Find the 4 orientations required for
    # the general and special cases
    o1 = intersection_orientation(p1, q1, p2)
    o2 = intersection_orientation(p1, q1, q2)
    o3 = intersection_orientation(p2, q2, p1)
    o4 = intersection_orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases

    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if (o1 == 0) and onSegment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if (o2 == 0) and onSegment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if (o3 == 0) and onSegment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if (o4 == 0) and onSegment(p2, q1, q2):
        return True

    # If none of the cases
    return False

def calculate_layer_distance(viewing_radius=None, paint_overlap=None):
    return viewing_radius * (1 - paint_overlap)

def calculate_viewing_radius(sensor_size=None, focal_length=None, altitude=None):
    fov = 2 * math.atan(sensor_size[1] / (2 * focal_length))
    viewing_radius = math.tan(fov / 2) * altitude
    return viewing_radius

def calculate_turn_directions(previous_waypoint=None, current_waypoint=None, next_waypoint=None):
    direction = intersection_orientation(previous_waypoint, current_waypoint, next_waypoint)
    if direction == 1:
        direction = "clockwise"
    elif direction == 2:
        direction = "counterclockwise"
    else:
        direction = "collinear"
    current_waypoint_turn_direction = direction
    next_waypoint_turn_direction = direction
    return current_waypoint_turn_direction, next_waypoint_turn_direction

def extend_point_to_match(point1=None, point2=None, direction=None):
    orientation_vector = create_point(Point(0, 0), 1, direction)

    point1_proj = get_projection(this_vector=point1, on_this_vector=orientation_vector)
    point2_proj = get_projection(this_vector=point2, on_this_vector=orientation_vector)
    proj_diff = abs(point1_proj - point2_proj)

    if point1_proj > point2_proj:
        furthest_point = point1
        extended_point = create_point(point2, proj_diff, direction)
    else:
        furthest_point = point2
        extended_point = create_point(point1, proj_diff, direction)

    return furthest_point, extended_point

def extend_point_to_match_original_order(point1=None, point2=None, direction=None):
    orientation_vector = create_point(Point(0, 0), 1, direction)

    point1_proj = get_projection(this_vector=point1, on_this_vector=orientation_vector)
    point2_proj = get_projection(this_vector=point2, on_this_vector=orientation_vector)
    proj_diff = abs(point1_proj - point2_proj)

    if point1_proj > point2_proj:
        point2 = create_point(point2, proj_diff, direction)
    else:
        point1 = create_point(point1, proj_diff, direction)

    return point1, point2

def calculate_furthest_point(point1=None, point2=None, direction=None):
    orientation_vector = create_point(Point(0, 0), 1, direction)

    point1_proj = get_projection(this_vector=point1, on_this_vector=orientation_vector)
    point2_proj = get_projection(this_vector=point2, on_this_vector=orientation_vector)

    if point1_proj > point2_proj:
        return point1, None
    else:
        return None, point2

def calculate_entrance_and_exit(current_waypoint=None, current_waypoint_centre_point=None, next_waypoint=None, next_waypoint_centre_point=None, turn_radius=None, direction=None, orientation=None, turn_type=None):
    current_waypoint_entrance = None
    current_waypoint_exit = None
    next_waypoint_entrance = None
    next_waypoint_exit = None

    current_direction, previous_point, next_next_point = calculate_current_direction(current_waypoint, next_waypoint, orientation, direction)

    # Check turn type
    if turn_type == "circle":
        current_waypoint_entrance, current_waypoint_exit = extend_point_to_match_original_order(current_waypoint, next_waypoint, current_direction)

    if turn_type == "double circle":
        # First turn
        entrance_angle, exit_angle = calculate_single_turn_entrance_exit(previous_waypoint=previous_point, current_waypoint=current_waypoint, next_waypoint=next_waypoint, direction=direction, radius=turn_radius)
        current_waypoint_entrance = create_point(current_waypoint_centre_point, turn_radius, entrance_angle)
        current_waypoint_exit = create_point(current_waypoint_centre_point, turn_radius, exit_angle)

        # Second turn
        entrance_angle, exit_angle = calculate_single_turn_entrance_exit(previous_waypoint=current_waypoint, current_waypoint=next_waypoint, next_waypoint=next_next_point, direction=direction, radius=turn_radius)
        next_waypoint_entrance = create_point(next_waypoint_centre_point, turn_radius, entrance_angle)
        next_waypoint_exit = create_point(next_waypoint_centre_point, turn_radius, exit_angle)

    if turn_type == "lightbulb":
        first_pair, middle_pair, third_pair = handle_entrance_exits_lightbulb(current_waypoint=current_waypoint, current_waypoint_centre_point=current_waypoint_centre_point, next_waypoint=next_waypoint, turn_radius=turn_radius, current_direction=current_direction)
        current_waypoint_entrance = [first_pair, middle_pair, third_pair]

    return current_waypoint_entrance, current_waypoint_exit, next_waypoint_entrance, next_waypoint_exit

def handle_entrance_exits_lightbulb(current_waypoint=None, current_waypoint_centre_point=None, next_waypoint=None, turn_radius=None, current_direction=None):
    current_waypoint, next_waypoint = extend_point_to_match_original_order(point1=current_waypoint, point2=next_waypoint, direction=current_direction)

    current_centre_to_middle_centre_angle = calculate_angle_from_points(from_point=current_waypoint_centre_point[0], to_point=current_waypoint_centre_point[1])
    current_centre_to_current_angle = calculate_angle_from_points(from_point=current_waypoint_centre_point[0], to_point=current_waypoint)

    next_centre_to_middle_centre_angle = calculate_angle_from_points(from_point=current_waypoint_centre_point[2], to_point=current_waypoint_centre_point[1])
    next_centre_to_next_angle = calculate_angle_from_points(from_point=current_waypoint_centre_point[2], to_point=next_waypoint)

    first_pair_entrance = create_point(current_waypoint_centre_point[0], turn_radius, current_centre_to_current_angle)
    first_pair_exit = create_point(current_waypoint_centre_point[0], turn_radius, current_centre_to_middle_centre_angle)
    first_pair = (first_pair_entrance, first_pair_exit)

    middle_pair_entrance = create_point(current_waypoint_centre_point[1], turn_radius, current_centre_to_middle_centre_angle + pi)
    middle_pair_exit = create_point(current_waypoint_centre_point[1], turn_radius, next_centre_to_middle_centre_angle + pi)
    middle_pair = (middle_pair_entrance, middle_pair_exit)

    third_pair_entrance = create_point(current_waypoint_centre_point[2], turn_radius, next_centre_to_middle_centre_angle)
    third_pair_exit = create_point(current_waypoint_centre_point[2], turn_radius, next_centre_to_next_angle)
    third_pair = (third_pair_entrance, third_pair_exit)

    return first_pair, middle_pair, third_pair

def calculate_current_direction(current_waypoint=None, next_waypoint=None, orientation=None, direction=None):
    # Find the two perpendicular unit vectors to orientation
    positive_perpendicular = create_point(current_waypoint, 1, orientation + pi / 2)
    negative_perpendicular = create_point(current_waypoint, 1, orientation - pi / 2)

    # Find which angle formed by the unit vectors and the current to next vector is smaller
    angle_between_positive = angle_between_points(next_waypoint, current_waypoint, positive_perpendicular)
    angle_between_negative = angle_between_points(next_waypoint, current_waypoint, negative_perpendicular)

    if angle_between_positive > angle_between_negative:
        if direction == "clockwise":
            current_direction = orientation + pi
        else:
            current_direction = orientation
    else:
        if direction == "clockwise":
            current_direction = orientation
        else:
            current_direction = orientation + pi

    previous_point = create_point(current_waypoint, 1, current_direction + pi)
    next_next_point = create_point(next_waypoint, 1, current_direction + pi)

    return clamp_angle(current_direction), previous_point, next_next_point

def calculate_single_turn_entrance_exit(previous_waypoint=None, current_waypoint=None, next_waypoint=None, direction=None, radius=None):
    angle_between = angle_between_points(previous_waypoint, current_waypoint, next_waypoint)
    bisector_angle = calculate_bisection_angle(previous_waypoint, current_waypoint, next_waypoint)
    centre_radius = radius / math.sin(angle_between / 2)

    # https://math.stackexchange.com/questions/797828/calculate-center-of-circle-tangent-to-two-lines-in-space
    centre_point = create_point(current_waypoint, centre_radius, bisector_angle)

    # https://math.stackexchange.com/questions/4629284/looking-for-a-formula-to-find-the-angle-to-a-point-that-creates-two-perpendicula
    centre_to_current_direction = calculate_angle_from_points(from_point=centre_point, to_point=current_waypoint)
    if direction == "clockwise":
        entrance_angle = centre_to_current_direction - (pi - angle_between / 2 - pi / 2)
        exit_angle = centre_to_current_direction + (pi - angle_between / 2 - pi / 2)
    else:
        entrance_angle = centre_to_current_direction + (pi - angle_between / 2 - pi / 2)
        exit_angle = centre_to_current_direction - (pi - angle_between / 2 - pi / 2)

    return entrance_angle, exit_angle

def create_centre_points(current_waypoint=None, next_waypoint=None, orientation=None, turn_radius=None, turn_type=None, direction=None, layer_distance=None):
    circle_centres = None, None

    current_direction, previous_point, next_next_point = calculate_current_direction(current_waypoint, next_waypoint, orientation, direction)
    if turn_type == "circle":
        if current_direction is not None:
            current_waypoint, next_waypoint = extend_point_to_match_original_order(current_waypoint, next_waypoint, current_direction)

        circle_centres = (Point((current_waypoint.x + next_waypoint.x) / 2, (current_waypoint.y + next_waypoint.y) / 2), None)

    if turn_type == "double circle":
        turn_point1 = calculate_single_centre_point(previous_point, current_waypoint, next_waypoint, turn_radius)
        turn_point2 = calculate_single_centre_point(current_waypoint, next_waypoint, next_next_point, turn_radius)
        circle_centres = (turn_point1, turn_point2)

    if turn_type == "lightbulb":
        circle_centres = create_centre_points_for_lightbulb(current_waypoint=current_waypoint, next_waypoint=next_waypoint, turn_direction=direction, turn_radius=turn_radius, layer_distance=layer_distance, current_direction=current_direction)

    return circle_centres

def create_centre_points_for_lightbulb(current_waypoint=None, next_waypoint=None, turn_direction=None, turn_radius=None, layer_distance=None, current_direction=None):
    current_waypoint, next_waypoint = extend_point_to_match_original_order(point1=current_waypoint, point2=next_waypoint, direction=current_direction)

    # The first and last centre points
    if turn_direction == "clockwise":
        current_waypoint_centre = create_point(current_waypoint, turn_radius, current_direction + pi / 2)
        next_waypoint_centre = create_point(next_waypoint, turn_radius, current_direction - pi / 2)
    else:
        current_waypoint_centre = create_point(current_waypoint, turn_radius, current_direction - pi / 2)
        next_waypoint_centre = create_point(next_waypoint, turn_radius, current_direction + pi / 2)

    # Find location of middle centre point
    centre_of_waypoints = Point((current_waypoint.x + next_waypoint.x) / 2, (current_waypoint.y + next_waypoint.y) / 2)
    distance_forwards = math.sqrt(4 * turn_radius ** 2 - (turn_radius + layer_distance / 2) ** 2)

    centre_x = centre_of_waypoints.x + distance_forwards * math.cos(current_direction)
    centre_y = centre_of_waypoints.y + distance_forwards * math.sin(current_direction)

    middle_centre = Point(centre_x, centre_y)
    circle_centres = ([current_waypoint_centre, middle_centre, next_waypoint_centre], None)
    return circle_centres

def calculate_single_centre_point(previous_waypoint=None, current_waypoint=None, next_waypoint=None, radius=None):
    angle_between = angle_between_points(previous_waypoint, current_waypoint, next_waypoint)
    bisector_angle = calculate_bisection_angle(previous_waypoint, current_waypoint, next_waypoint)
    centre_radius = radius / math.sin(angle_between / 2)

    centre_point = create_point(current_waypoint, centre_radius, bisector_angle)
    return centre_point

def on_same_axis(point1=None, point2=None, orientation=None):
    angle_from_points = math.atan2(point1.y - point2.y, point1.x - point2.x)

    if round(angle_from_points, 10) == round(orientation, 10) or round(clamp_angle(angle_from_points + pi), 10) == round(orientation, 10):
        return True
    else:
        return False

def determine_turn_type(layer_distance=None, turn_radius=None):
    if 2 * turn_radius < layer_distance:
        if 4 * turn_radius < layer_distance:
            return "double circle", "double circle"
        else:
            return "circle", "circle"
    else:
        return "lightbulb", "lightbulb"

def create_waypoints_from_points(points=None):
    waypoints = []
    for point in points:
        new_waypoint = Waypoint(point.x, point.y)
        waypoints.append(new_waypoint)
    return waypoints

def calculate_closest_point_on_segment_to_point(segment_start=None, segment_end=None, reference_point=None):
    segment_vector = Point(segment_end.x - segment_start.x, segment_end.y - segment_start.y)
    segment_to_reference = Point(reference_point.x - segment_start.x, reference_point.y - segment_start.y)
    percentage_along_segment = (segment_to_reference.x * segment_vector.x + segment_to_reference.y * segment_vector.y) / (segment_vector.x ** 2 + segment_vector.y ** 2)
    percentage_along_segment = max(0, min(percentage_along_segment, 1))
    closest_point = Point(segment_start.x + percentage_along_segment * segment_vector.x, segment_start.y + percentage_along_segment * segment_vector.y)
    return closest_point

def clamp_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))

def calculate_closest_perpendicular_vertex(polygon=None, orientation=None, start_point=None):
    perpendicular_direction = Point(math.sin(orientation), - math.cos(orientation))
    furthest_vertices = [0, 0]
    furthest_projections = [0, 0]
    vertex_count = 0
    for vertex in polygon.vertices:
        starting_to_vertex = Point(vertex.x - start_point.x, vertex.y - start_point.y)
        projection = starting_to_vertex.dot(perpendicular_direction) / perpendicular_direction.magnitude() ** 2
        if projection < furthest_projections[0]:
            furthest_vertices[0] = vertex_count
            furthest_projections[0] = projection
        if projection > furthest_projections[1]:
            furthest_vertices[1] = vertex_count
            furthest_projections[1] = projection
        vertex_count += 1
    # Find the closest point of the furthest vertices
    left_point_dist = calculate_distance_between_points(polygon.vertices[furthest_vertices[0]], start_point)
    right_point_dist = calculate_distance_between_points(polygon.vertices[furthest_vertices[1]], start_point)
    if left_point_dist < right_point_dist:
        closest_point = polygon.vertices[furthest_vertices[0]]
        closest_vertex = furthest_vertices[0]
    else:
        closest_point = polygon.vertices[furthest_vertices[1]]
        closest_vertex = furthest_vertices[1]
    return closest_point, closest_vertex

def calculate_point_away_from_polygon(polygon=None, centre_vertex_index=None, distance=None):
    centre_vertex = polygon.vertices[centre_vertex_index]
    next_vertex = polygon.vertices[(centre_vertex_index + 1) % polygon.count]
    prev_vertex = polygon.vertices[(centre_vertex_index + polygon.count - 1) % polygon.count]

    bisection_angle = calculate_bisection_angle(prev_vertex, centre_vertex, next_vertex)

    path_start = Point(centre_vertex.x + distance * math.cos(bisection_angle),
                       centre_vertex.y + distance * math.sin(bisection_angle))
    return path_start

def angle_between_points(pointA=None, pointB=None, pointC=None):
    AB = Point(pointB.x - pointA.x, pointB.y - pointA.y)
    BC = Point(pointC.x - pointB.x, pointC.y - pointB.y)
    if AB.dot(BC) / (AB.magnitude() * BC.magnitude()) > 1 or AB.dot(BC) / (AB.magnitude() * BC.magnitude()) < -1:
        angle = pi
        return angle

    angle = math.acos(AB.dot(BC) / (AB.magnitude() * BC.magnitude()))
    return angle + pi

def calculate_bisection_angle(point_A=None, point_B=None, point_C=None, acute=True):
    angle_to_A = math.atan2(point_A.y - point_B.y, point_A.x - point_B.x)
    angle_to_C = math.atan2(point_C.y - point_B.y, point_C.x - point_B.x)
    angle_diff = abs(angle_to_A - angle_to_C)
    average = (angle_to_A + angle_to_C) / 2

    if angle_diff > pi:
        bisection_angle = average - pi
    else:
        bisection_angle = average

    return clamp_angle(bisection_angle)

def calculate_closest_point_on_polygon(polygon=None, start_point=None):
    # Loop over each segment of search area
    closest_point = None
    closest_distance = None
    for index in range(len(polygon.vertices)):
        segment_point_1 = polygon.vertices[index]
        segment_point_2 = polygon.vertices[(index + 1) % len(polygon.vertices)]
        # Find the closest point on segment to start location
        new_closest_point = calculate_closest_point_on_segment_to_point(segment_point_1, segment_point_2, start_point)
        new_closest_distance = calculate_distance_between_points(new_closest_point, start_point)
        if closest_point is None or new_closest_distance < closest_distance:
            closest_point = new_closest_point
            closest_distance = new_closest_distance
    return closest_point

def calculate_points_along_polygon_distanced(start_point=None, polygon=None, orientation=None, layer_distance=None, direction=None):
    rough_waypoints = [start_point]
    count = 0
    max_points = 100
    if direction == "forward":
        directions = ["forward", "left"]  # 0 index is current direction to go, 1 index is previous direction travelled
    else:
        directions = ["forward", "left"]
    new_point = None
    while count < max_points:
        # If the current direction in direction of orientation or backwards, raycast then backtrack by layer distance
        if directions[0] == "forward":
            new_point = handle_forward_backward_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation, layer_distance=layer_distance)
        elif directions[0] == "backward":
            new_point = handle_forward_backward_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=clamp_angle(orientation + pi), layer_distance=layer_distance)
        elif directions[0] == "left":
            if directions[1] == "forward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation + pi / 2, layer_distance=layer_distance, raycast_direction=orientation)
            elif directions[1] == "backward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation - pi / 2, layer_distance=layer_distance, raycast_direction=orientation + pi)
        else:  # directions[0] == "right":
            if directions[1] == "forward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation - pi / 2, layer_distance=layer_distance, raycast_direction=orientation)
            else:  # directions[1] == "backward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation + pi / 2, layer_distance=layer_distance, raycast_direction=orientation + pi)

        # If reached the end of the path
        if new_point is None:
            return rough_waypoints

        # If the new point is the same as the previous point, disregard it
        if new_point != rough_waypoints[-1]:
            rough_waypoints.append(new_point)

        count += 1
        if directions == ["forward", "left"]:
            directions = ["right", "forward"]
        elif directions == ["right", "forward"]:
            directions = ["backward", "right"]
        elif directions == ["backward", "right"]:
            directions = ["left", "backward"]
        elif directions == ["left", "backward"]:
            directions = ["forward", "left"]

        elif directions == ["forward", "right"]:
            directions = ["left", "forward"]
        elif directions == ["left", "forward"]:
            directions = ["backward", "left"]
        elif directions == ["backward", "left"]:
            directions = ["right", "backward"]
        elif directions == ["right", "backward"]:
            directions = ["forward", "right"]

    return rough_waypoints

def get_projection(this_vector=None, on_this_vector=None):
    projection = this_vector.dot(on_this_vector) / on_this_vector.magnitude() ** 2
    return projection

def handle_forward_backward_direction(origin=None, polygon=None, orientation=None, layer_distance=None):
    raycast_point = raycast_to_polygon(origin=origin, polygon=polygon, direction=orientation)
    if raycast_point is None:
        return None
    # TODO: Distancing the point like this doesn't really work for slanted surfaces
    distant_point = create_point(raycast_point, layer_distance, orientation + pi)

    # Make sure the distant point is not behind the origin point
    forward_direction = create_point(Point(0, 0), 1, orientation)
    reference_point = Point(distant_point.x - origin.x, distant_point.y - origin.y)

    projection = get_projection(this_vector=reference_point, on_this_vector=forward_direction)
    if projection <= 0:
        return origin

    return distant_point

def handle_sideways_direction(origin=None, polygon=None, orientation=None, layer_distance=None, raycast_direction=None):
    distant_point = create_point(origin, layer_distance, orientation)
    raycast_point = raycast_to_polygon(origin=distant_point, direction=raycast_direction, polygon=polygon)
    if raycast_point is None:
        raycast_point = find_closest_intersection_point(ray_origin=distant_point, ray_direction=raycast_direction + pi, polygon=polygon)
        if raycast_point is None:
            return None
    distanced_raycast = create_point(raycast_point, layer_distance, raycast_direction + pi)

    # If the point is within the polygon, return it. It's a good point
    if polygon.contains(distanced_raycast):
        return distanced_raycast
    return None

def find_closest_vertex_index(polygon=None, point=None):
    closest_vertex_index = None
    closest_vertex_distance = float('inf')
    for index, vertex in enumerate(polygon.vertices):
        distance = calculate_distance_between_points(point, vertex)
        if distance < closest_vertex_distance:
            closest_vertex_index = index
            closest_vertex_distance = distance
    return closest_vertex_index

def create_segments_from_polygon(vertices=None):
    segments = []
    num_vertices = len(vertices)

    for i in range(num_vertices):
        start = vertices[i]
        end = vertices[(i + 1) % num_vertices]
        segment = Segment(start, end)
        segments.append(segment)

    return segments

def find_closest_intersection_point(ray_origin=None, ray_direction=None, polygon=None):
    # Create ray
    ray_end = create_point(ray_origin, polygon.maximum, ray_direction)
    ray = Segment(ray_origin, ray_end)

    # Get the indices of which segments intersect
    indices_list = []
    for index, segment in enumerate(polygon.segments):
        if do_segments_intersect(ray, segment):
            indices_list.append(index)

    # Loop through segments that intersect and find the closest intersection point
    minimum_found_intersection_point = None
    minimum_found_distance = polygon.maximum
    for index in indices_list:
        intersection_point = find_segment_intersection(ray, polygon.segments[index])
        distance_to_point = calculate_distance_between_points(ray_origin, intersection_point)
        if distance_to_point <= minimum_found_distance:
            minimum_found_intersection_point = intersection_point
            minimum_found_distance = distance_to_point

    return minimum_found_intersection_point

def create_point(point=None, dist=None, angle=None):
    return Point(point.x + dist * math.cos(angle), point.y + dist * math.sin(angle))

def find_segment_intersection(segment1, segment2):
    xdiff = Point(segment1.start.x - segment1.end.x, segment2.start.x - segment2.end.x)
    ydiff = Point(segment1.start.y - segment1.end.y, segment2.start.y - segment2.end.y)

    def det(a, b):
        return a.x * b.y - a.y * b.x

    div = det(xdiff, ydiff)
    if div == 0:
        return None

    d = Point(det(segment1.start, segment1.end), det(segment2.start, segment2.end))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return Point(x, y)

def create_random_search_area(vertex_count, x_lim=None, y_lim=None):
    if y_lim is None:
        y_lim = [0, 10]
    if x_lim is None:
        x_lim = [0, 10]
    x_diff = x_lim[1] - x_lim[0]
    y_diff = y_lim[1] - y_lim[0]
    max_dist = math.sqrt(x_diff ** 2 + y_diff ** 2)
    vertices = []

    angle_percentages = []
    for index in range(vertex_count):
        angle_percentages.append(random.random())

    angle_percentages.sort()

    for index in range(vertex_count):
        angle = angle_percentages[index] * 2*pi
        vertex = Point(x_diff + max_dist * math.cos(angle), y_diff + max_dist * math.sin(angle))
        vertices.append(vertex)
    search_area = Polygon(vertices=vertices)
    return search_area

def create_random_layer_distance(limits=None):
    if limits is None:
        limits = [0.1, 1]
    layer_distance = random.uniform(limits[0], limits[1])
    return layer_distance

def create_random_start_point(x_lim=None, y_lim=None):
    if y_lim is None:
        y_lim = [0, 10]
    if x_lim is None:
        x_lim = [0, 10]

    x_diff = x_lim[1] * 2 - x_lim[0] * 2
    y_diff = y_lim[1] * 2 - y_lim[0] * 2

    random_start = Point(random.uniform(x_diff - abs(x_diff) / 2, x_diff + abs(x_diff) / 2), random.uniform(y_diff - abs(y_diff) / 2, y_diff + abs(y_diff) / 2))
    return random_start

def calculate_distance_between_points(point_1=None, point_2=None):
    return math.sqrt((point_1.x - point_2.x) ** 2 + (point_1.y - point_2.y) ** 2)

def print_waypoints(waypoints=None):
    for index, waypoint in enumerate(waypoints):
        print(index, " | ", waypoint.x, waypoint.y)

def do_entire_simulation(do_plot=True):
    search_area_polygon = create_random_search_area(7)
    layer_distance = create_random_layer_distance([0.5, 5])
    start_point = create_random_start_point()

    raw_waypoints = [[0, 0], [2, 4], [5, 2], [3, -2], [6, -2], [3, -5], [1, -4]]
    minimum_turn_radius = 1
    # search_area = [[0, 0], [-4, 4], [0, 10], [10, 8], [14, 2]]
    # search_area = [[0, 0], [0, 10], [10, 10], [10, 0]]
    # search_area = [[0, 0], [-4, 4], [0, 10], [10, 8], [14, 2]]
    curve_resolution = 4
    # start_point = Point(6, 14)
    sensor_size = (12.8, 9.6)
    focal_length = 16
    paint_overlap = 0.1
    angle = None

    path_generator = SearchPathGenerator()
    path_generator.set_data(search_area=search_area_polygon)
    path_generator.set_parameters(orientation=angle, paint_overlap=paint_overlap, focal_length=None, sensor_size=None, minimum_turn_radius=minimum_turn_radius, layer_distance=layer_distance, curve_resolution=curve_resolution, start_point=None)

    path_generator.generate_path(do_plot=do_plot)
    return path_generator.error

def run_number_of_sims(count=None, plot=None):
    error_count = 0
    for index in range(count):
        if index % math.ceil(count / 10) == 0:
            print("Progress:", index / count * 100, "% |", index, "/", count)
        error = do_entire_simulation(do_plot=plot)
        if error:
            error_count += 1

    print("Simulation Complete | Error count:", error_count, "/", count, "| Error percentage:", error_count / count * 100, "%")

def main_function():
    run_number_of_sims(10000, plot=False)

    # raw_waypoints = [[0, 0], [2, 4], [5, 2], [3, -2], [6, -2], [3, -5], [1, -4]]
    # minimum_turn_radius = 2.5
    # search_area = [[11.423, 24.070], [20.304, 24.139], [25.507, -0.470], [19.660, -0.329], [10, 1.617], [5, 2.745], [2.5, 7.510]]
    # # search_area = [[0, 0], [0, 10], [10, 10], [10, 0]]
    # # search_area = [[0, 0], [-4, 4], [0, 10], [10, 8], [14, 2]]
    # curve_resolution = 4
    # start_point = Point(26.637, 23.066)
    # sensor_size = (12.8, 9.6)
    # focal_length = 16
    # paint_overlap = 0.1
    # angle = None
    # layer_distance = 4
    #
    # points = []
    # for point in search_area:
    #     points.append(Point(point[0], point[1]))
    # search_area_polygon = Polygon(points)
    #
    # path_generator = SearchPathGenerator()
    # path_generator.set_data(search_area=search_area_polygon)
    # path_generator.set_parameters(orientation=angle, paint_overlap=paint_overlap, focal_length=focal_length, sensor_size=sensor_size, minimum_turn_radius=minimum_turn_radius, layer_distance=layer_distance, curve_resolution=curve_resolution, start_point=start_point)
    #
    # path_generator.generate_path(do_plot=True)


if __name__ == "__main__":
    main_function()
