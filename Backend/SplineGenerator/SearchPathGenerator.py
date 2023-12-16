from __future__ import division, print_function

import time
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
            x_sum += vertex.lon
            y_sum += vertex.lat
        x_avg = x_sum / self.count
        y_avg = y_sum / self.count
        centroid = Coord(lon=x_avg, lat=y_avg)
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
        self.coords = Coord(lon=x, lat=y)  # Point instance that stores location of waypoint
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


class SearchPathGenerator:
    def __init__(self):
        pass

    # Input Data (points and boundaries)
    raw_waypoints = None  # List of rough waypoints to travel through
    search_area = None  # Polygon class instance that defines the boundary of the search area the plane will scan
    boundary = None  # Polygon class instance that defines the boundary that the path must remain in. Path can be on the boundary
    take_off_point = None  # Point where the Albatross takes off
    landing_point = None  # Point where the Albatross should land
    alt = None  # Altitude the path will be generated at

    # Input Parameters
    turn_radius = None  # The minimum turning radius of the plane at cruise speed in metres
    boundary_resolution = None  # A factor inversely proportional to the step size that the path will adjust to avoid the boundary
    boundary_tolerance = None  # The minimum distance from the boundary the path must remain
    orientation = None  # Desired axis of orientation set by the user or calculated as the most efficient
    curve_resolution = None  # How many waypoints per metre we want
    max_flight_time = None  # The maximum amount of flight time
    sensor_size = None  # (width, height) in mm
    focal_length = None  # Lens focal length in mm
    paint_overlap = 0.2  # Minimum paint overlap required in terms of percentage. Must be less than 100%
    paint_radius = None  # The radius in metres around the plane that the cameras can see / paint
    perimeter_distance = None  # The distance rough points will be placed from the search area perimeter
    layer_distance = None  # Distance between each 'layer' of the flight path
    turn_type = None  # Turn type for the turns in search area mode
    search_area_coverage = None  # Coverage of search area in fraction that the plane can see if following the current path points

    error = False  # Flag for if an error occurred during runtime
    first_waypoint_index = 0  # Holds the index of the first waypoint after the take off points

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
            new_point = Coord(lon=waypoint["long"], lat=waypoint["lat"])
            points.append(new_point)

        search_area = Polygon(points)
        self.search_area = search_area

    def get_waypoints(self):
        """
        Call this function to get a dictionary of every point in the path. The format is as follows:
        [{"lon": 101.24, "lat": 62.76, "alt": 100}, {"lon": 98.64, "lat": 65.22, "alt": 100}, ...]
        """
        dict_list = []

        for point in self.path_points:
            new_dict_entry = {"long": point.lon, "lat": point.lat, "alt": self.alt, "id": 16}
            dict_list.append(new_dict_entry)

        return dict_list

    def set_data(self, raw_waypoints=None, search_area=None, boundary=None):
        if raw_waypoints is not None:
            self.raw_waypoints = raw_waypoints
        if search_area is not None:
            self.search_area = search_area
        if boundary is not None:
            self.boundary = boundary

    def set_parameters(self, alt=None, minimum_turn_radius=None, boundary_resolution=None, layer_distance=None, boundary_tolerance=None, curve_resolution=None, orientation=None, start_point=None, focal_length=None, sensor_size=None, paint_overlap=None):
        if alt is not None:
            self.alt = alt
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

    def check_parameter_accounted(self):
        missing_parameters = []
        # Check essential parameters
        if self.search_area is None:
            missing_parameters.append("Search area")
        if self.alt is None:
            missing_parameters.append("Altitude")
        if self.turn_radius is None:
            missing_parameters.append("Turn radius")
        if self.curve_resolution is None:
            missing_parameters.append("Curve resolution")
        if self.sensor_size is None and self.focal_length is None and self.layer_distance is None:
            if self.layer_distance is None:
                if self.sensor_size is None:
                    missing_parameters.append("Sensor size")
                if self.focal_length is None:
                    missing_parameters.append("Focal length")
            else:
                missing_parameters.append("Layer distance")

        if len(missing_parameters) > 0:
            return False, missing_parameters

        return True, None

    def generate_search_area_path(self, do_plot=True):
        # Initial checks
        all_parameters_accounted_for, missing_parameters = self.check_parameter_accounted()
        if not all_parameters_accounted_for:
            self.path_points = {"Error": "Parameters missing", "Parameters": missing_parameters}
            return self.path_points

        # Pre-algorithm calculations
        if self.sensor_size is not None and self.focal_length is not None and self.layer_distance is None:
            self.paint_radius = calculate_viewing_radius(sensor_size=self.sensor_size, focal_length=self.focal_length, altitude=100)
            self.layer_distance = calculate_layer_distance(viewing_radius=self.paint_radius, paint_overlap=self.paint_overlap)
        if self.orientation is None:
            self.orientation = calculate_best_orientation(polygon=self.search_area)

        if self.orientation > 0:
            self.orientation -= pi

        # Complete pre-calculation data and parameter validation checks
        validation, error_message = self.do_pre_validation_checks()
        if validation is None:
            print(error_message)
            self.error = True
            return validation, error_message

        # Generate path points
        rough_points = self.generate_points()
        self.smooth_rough_points(rough_points=rough_points)

        # Check if path waypoints is none meaning no waypoints could be produced for the case
        if self.path_waypoints is None:
            return None, "No path waypoints could be produced for the given case..."

        # Check if only one or fewer waypoints are made
        if len(self.path_waypoints) <= 1:
            return None, "Only one waypoint..."

        # If a take-off point was specified, generate the points to get the plane from take-off to first waypoint
        if self.take_off_point is not None:
            # Determine the end orientation for this set of points
            if self.path_waypoints[0].curve_waypoints is not None:
                # Curves start on the first waypoint
                curve_start_index = 0
            else:
                # Curve start on the second waypoint
                curve_start_index = 1

            # Check if curve waypoints exist at this index
            if self.path_waypoints[curve_start_index].curve_waypoints is not None:
                if type(self.path_waypoints[curve_start_index].curve_waypoints[0]) == list:
                    # Lightbulb turn at the start
                    angle_from_centre_to_coord = calculate_angle_from_points(from_point=self.path_waypoints[curve_start_index].centre_point[0], to_point=self.path_waypoints[curve_start_index].curve_waypoints[0][0])
                    if self.path_waypoints[curve_start_index].turn_direction == "clockwise":
                        end_orientation = angle_from_centre_to_coord + pi / 2
                    else:
                        end_orientation = angle_from_centre_to_coord - pi / 2
                else:
                    # Circle turn
                    angle_from_centre_to_coord = calculate_angle_from_points(from_point=self.path_waypoints[curve_start_index].centre_point, to_point=self.path_waypoints[curve_start_index].curve_waypoints[0])

                    if self.path_waypoints[curve_start_index].turn_direction == "clockwise":
                        end_orientation = angle_from_centre_to_coord - pi / 2
                    else:
                        end_orientation = angle_from_centre_to_coord + pi / 2

                take_off_points = generate_points_to(start_point=self.take_off_point, end_point=rough_points[0], end_orientation=end_orientation, radius=self.turn_radius, curve_resolution=self.curve_resolution)
                if take_off_points is not None:
                    self.first_waypoint_index = len(take_off_points)
            else:
                take_off_points = None
        else:
            take_off_points = None

        # Calculate callable point
        self.path_points = self.calculate_path_points()

        # Add take off points if they exist
        if take_off_points is not None and self.path_points is not None:
            self.path_points = take_off_points + self.path_points

        # Complete post-calculation data validation checks
        if rough_points is not None:
            validation, error_message = self.do_post_validation_checks(waypoints=rough_points)
        if do_plot:
            # print_waypoints(rough_points)
            self.plot_waypoints(waypoints=rough_points, polygon=self.search_area, actual_waypoints=self.path_waypoints)
            self.plot_points(points=self.path_points, polygon=self.search_area, actual_waypoints=self.path_waypoints)
        if validation is None:
            self.error = error_message
            self.print_debug()

    def plot_points(self, points=None, polygon=None, actual_waypoints=None):
        plt.figure(dpi=200)  # Resolution for zoomin in

        # Plot original waypoints if given
        if actual_waypoints is not None:
            x_original = [point.coords.lon for point in actual_waypoints]
            y_original = [point.coords.lat for point in actual_waypoints]
            plt.scatter(x_original, y_original, color='black')

        # Plot all points
        x_vals = [point.lon for point in points]
        y_vals = [point.lat for point in points]
        plt.plot(x_vals, y_vals, color='red')
        plt.scatter(x_vals, y_vals, color='b', s=13)

        # Plot polygon if given
        if polygon is not None:
            x_polygon = [point.lon for point in polygon.vertices]
            x_polygon.append(polygon.vertices[0].lon)
            y_polygon = [point.lat for point in polygon.vertices]
            y_polygon.append(polygon.vertices[0].lat)
            plt.plot(x_polygon, y_polygon, color='black')

        if self.take_off_point is not None:
            plt.scatter(self.take_off_point.lon, self.take_off_point.lat, marker='^', color='black')
            plt.annotate("Takeoff", (self.take_off_point.lon, self.take_off_point.lat), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.annotate("First Waypoint", (self.path_points[self.first_waypoint_index].lon, self.path_points[self.first_waypoint_index].lat), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.annotate("Final Waypoint", (self.path_points[-1].lon, self.path_points[-1].lat), textcoords="offset points", xytext=(0, 10), ha='center')

        # Plot it all
        plt.axis('equal')
        plt.show()

    def calculate_path_points(self):
        if self.path_waypoints is None:
            return None

        points = []
        # Add the first waypoint's coords if it doesn't begin with a turn
        if self.path_waypoints[0].centre_point is None:
            points.append(self.path_waypoints[0].coords)
        elif type(self.path_waypoints[0].curve_waypoints[0]) == list:
            # Lightbulb turn
            if not self.path_waypoints[0].curve_waypoints[0][0].equals(self.path_waypoints[0].coords):
                points.append(self.path_waypoints[0].coords)
        else:
            # Circle or double circle turn
            if not self.path_waypoints[0].curve_waypoints[0].equals(self.path_waypoints[0].coords):
                points.append(self.path_waypoints[0].coords)

        for waypoint in self.path_waypoints:

            if waypoint.curve_waypoints is not None:
                if type(waypoint.curve_waypoints[0]) == list:
                    # Lightbulb turn
                    for turn in waypoint.curve_waypoints:
                        for point in turn:
                            points.append(point)
                else:
                    for point in waypoint.curve_waypoints:
                        points.append(point)

        # Add the final waypoint's coords if it doesn't end in a turn
        if self.path_waypoints[-1].centre_point is None:
            points.append(self.path_waypoints[-1].coords)
        elif type(self.path_waypoints[-1].curve_waypoints[0]) == list:
            # Lightbulb turn
            if not self.path_waypoints[-1].curve_waypoints[0][0].equals(self.path_waypoints[-1].coords):
                points.append(self.path_waypoints[-1].coords)
        else:
            # Circle or double circle turn
            if not self.path_waypoints[-1].curve_waypoints[0].equals(self.path_waypoints[-1].coords):
                points.append(self.path_waypoints[-1].coords)

        return points

    def print_debug(self):
        print("ERROR:", self.error)
        print("\tSearch Area:")
        for vertex in self.search_area.vertices:
            print("\t\t", vertex.lon, vertex.lat)
        print("\tStart Point:")
        print("\t\t", self.take_off_point.lon, self.take_off_point.lat)
        print("\tLayer Distance:")
        print("\t\t", self.layer_distance)
        print("\tTurn Radius:")
        print("\t\t", self.turn_radius)

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
            poly_x.append(point.lon)
            poly_y.append(point.lat)
        poly_x.append(polygon.vertices[0].lon)
        poly_y.append(polygon.vertices[0].lat)
        plt.plot(poly_x, poly_y, color='black')

        x_vals = []
        y_vals = []
        for point in waypoints:
            x_vals.append(point.lon)
            y_vals.append(point.lat)
        plt.plot(x_vals, y_vals, color='blue')
        plt.scatter(x_vals, y_vals, color='blue')

        x_centre = []
        y_centre = []
        for waypoint in actual_waypoints:
            if waypoint.centre_point is not None:
                if type(waypoint.centre_point) == list:
                    for point in waypoint.centre_point:
                        x_centre.append(point.lon)
                        y_centre.append(point.lat)
                else:
                    x_centre.append(waypoint.centre_point.lon)
                    y_centre.append(waypoint.centre_point.lat)
        if len(x_centre) > 0:
            plt.scatter(x_centre, y_centre, color='orange')

        x_entrance = []
        y_entrance = []
        x_exit = []
        y_exit = []
        for waypoint in actual_waypoints:
            if waypoint.entrance is not None:
                x_entrance.append(waypoint.entrance.lon)
                y_entrance.append(waypoint.entrance.lat)
                x_exit.append(waypoint.exit.lon)
                y_exit.append(waypoint.exit.lat)
            if waypoint.lightbulb_pairs is not None:
                for pair in waypoint.lightbulb_pairs:
                    x_entrance.append(pair[0].lon)
                    y_entrance.append(pair[0].lat)
                    x_exit.append(pair[1].lon)
                    y_exit.append(pair[1].lat)
        if len(x_entrance) > 0:
            plt.scatter(x_entrance, y_entrance, color='green')
            plt.scatter(x_exit, y_exit, color='green')


        plt.scatter(waypoints[0].lon, waypoints[0].lat, color='red')
        plt.annotate("First waypoint", (waypoints[0].lon, waypoints[0].lat), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.scatter(self.search_area.centroid.lon, self.search_area.centroid.lat, color='purple')
        plt.annotate("Centre of calculations", (self.search_area.centroid.lon, self.search_area.centroid.lat), textcoords="offset points", xytext=(0, 10), ha='center')
        if self.take_off_point is not None:
            plt.scatter(self.take_off_point.lon, self.take_off_point.lat, marker='^', color='black')
            plt.annotate("Takeoff", (self.take_off_point.lon, self.take_off_point.lat), textcoords="offset points", xytext=(0, 10), ha='center')

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

        # Check if there are any duplicate consecutive path points
        validation_flag, error_message = self.validation_duplicate_path_points(self.path_points)
        if validation_flag is None:
            return validation_flag, error_message

        return "All g", "All g"

    def validation_duplicate_path_points(self, path_points):
        for index in range(len(path_points) - 1):
            point1 = path_points[index]
            point2 = path_points[index + 1]
            if point1.equals(point2):
                return None, "Two consecutive points are equal"

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
                    print("INTERSECTION:", edge1.start.lon, edge1.start.lat)
                    print("INTERSECTION:", edge1.end.lon, edge1.end.lat)
                    print("INTERSECTION:", edge2.start.lon, edge2.start.lat)
                    print("INTERSECTION:", edge2.end.lon, edge2.end.lat)
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
            if distance_end > distance_start:
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

def generate_points_to(start_point=None, end_point=None, end_orientation=None, radius=None, curve_resolution=None):
    # Determine which direction the plane will rotate in
    point_just_behind_end_point = create_point(end_point, 1, end_orientation + pi)
    turn_direction, temp = calculate_turn_directions(previous_waypoint=start_point, current_waypoint=point_just_behind_end_point, next_waypoint=end_point)

    # Create centre point at correct angle
    if turn_direction == "clockwise":
        centre_point = create_point(end_point, radius, end_orientation - pi / 2)
    else:
        centre_point = create_point(end_point, radius, end_orientation + pi / 2)
    # Define entrance and exit angles
    entrance_angle, exit_angle = calculate_entrance_and_exit_end_on_waypoint(start_point=start_point, centre_point=centre_point, radius=radius, direction=turn_direction)

    # The radius is bigger than the distance from the take-off point to the first waypoint, then return none
    if entrance_angle is None:
        return None

    # Get the curve points
    curve_points = general_curve_interpolation(start_angle=entrance_angle, end_point=end_point, centre_point=centre_point, radius=radius, turn_direction=turn_direction, curve_resolution=curve_resolution)
    # Create list of points from start to end
    points = [start_point] + curve_points
    return points

def general_curve_interpolation(start_point=None, start_angle=None, end_point=None, end_angle=None, centre_point=None, radius=None, turn_direction=None, curve_resolution=None):
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

def calculate_entrance_and_exit_end_on_waypoint(start_point=None, centre_point=None, radius=None, direction=None):
    distance = calculate_distance_between_points(start_point, centre_point)
    alpha = math.atan2(start_point.lat - centre_point.lat, start_point.lon - centre_point.lon)

    if not -1 <= radius / distance <= 1:
        return None, None

    theta1 = math.acos(radius / distance) + alpha
    theta2 = math.acos(radius / distance) - alpha

    if direction == "clockwise":
        return -theta2, theta1
    else:
        return theta1, -theta2

def calculate_curve_waypoints_for_lightbulb(waypoint=None, curve_resolution=None, radius=None):
    if waypoint.turn_direction == "clockwise":
        centre_direction = "clockwise"
        side_direction = "counterclockwise"
    else:
        centre_direction = "counterclockwise"
        side_direction = "clockwise"

    # Calculate the angle step for the entire three turns here. This is to ensure the distances between curve waypoints are the same
    angle_step = calculate_angle_step(centre_points=waypoint.centre_point, entrance_exits=waypoint.lightbulb_pairs, turn_radius=radius, curve_resolution=curve_resolution, initial_turn_direction=side_direction)

    first_turn_points, ending_angle, leftover = curve_interpolation(centre_point=waypoint.centre_point[0], entrance_point=waypoint.lightbulb_pairs[0][0], exit_point=waypoint.lightbulb_pairs[0][1], turn_radius=radius, turn_direction=side_direction, angle_step=angle_step, initial_angle=0, previous_leftover=0)
    middle_turn_points, ending_angle, leftover = curve_interpolation(centre_point=waypoint.centre_point[1], entrance_point=waypoint.lightbulb_pairs[1][0], exit_point=waypoint.lightbulb_pairs[1][1], turn_radius=radius, turn_direction=centre_direction, angle_step=angle_step, initial_angle=ending_angle, previous_leftover=leftover)
    third_turn_points, ending_angle, leftover = curve_interpolation(centre_point=waypoint.centre_point[2], entrance_point=waypoint.lightbulb_pairs[2][0], exit_point=waypoint.lightbulb_pairs[2][1], turn_radius=radius, turn_direction=side_direction, angle_step=angle_step, initial_angle=ending_angle, previous_leftover=leftover)

    return [first_turn_points, middle_turn_points, third_turn_points]

def calculate_angle_step(centre_points=None, entrance_exits=None, turn_radius=None, curve_resolution=None, initial_turn_direction=None):
    # Calculate the total amount of angle the plane will rotate about its yaw throughout the lightbulb turn
    total_angle = 0

    direction_list = ["clockwise", "counterclockwise"]
    if initial_turn_direction == "counterclockwise":
        direction_list.reverse()

    # Add up the angle differences for each turn
    for index in range(3):
        # Find start angle
        start_angle = calculate_angle_from_points(from_point=centre_points[index], to_point=entrance_exits[index][0])

        # Find end angle
        end_angle = calculate_angle_from_points(from_point=centre_points[index], to_point=entrance_exits[index][1])

        # Find inbetween angle based on turn direction
        if direction_list[index % 2] == "clockwise":
            angle_difference = start_angle - end_angle
        else:
            angle_difference = end_angle - start_angle

        if angle_difference < 0.0:
            angle_difference += 2 * pi

        total_angle += angle_difference

    # Calculate the circumference travelled due to the angle difference
    distance = turn_radius * total_angle

    # Calculate the number of points required due to the curve resolution
    number_of_points = int(math.ceil(distance * curve_resolution))

    # Calculate the angle step for the given number of points
    angle_step = total_angle / number_of_points

    return angle_step

def curve_interpolation(centre_point=None, entrance_point=None, exit_point=None, turn_radius=None, turn_direction=None, angle_step=None, initial_angle=None, previous_leftover=None):
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
    elif angle_difference > 2 * pi:
        angle_difference -= 2 * pi

    # Find angle step
    # number_of_points, angle_step = calculate_angle_step_for_curve_interpolation(curve_resolution=curve_resolution, radius=turn_radius, angle_difference=angle_difference)

    # Clockwise or counter-clockwise for angle step
    if turn_direction == "clockwise":
        angle_step = - angle_step
        current_angle = start_angle - previous_leftover
        angle_counter = initial_angle + previous_leftover
    else:
        current_angle = start_angle + previous_leftover
        angle_counter = initial_angle + previous_leftover

    # Loop through and make the waypoints
    curve_waypoints = []
    while angle_counter <= angle_difference + initial_angle:
        new_point = create_point(centre_point, turn_radius, current_angle)
        curve_waypoints.append(new_point)
        current_angle += angle_step
        angle_counter += abs(angle_step)

    leftover = angle_counter - (angle_difference + initial_angle)
    return curve_waypoints, angle_counter, leftover

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
    for index in range(number_of_points + 1):
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
    y = to_point.lat - from_point.lat
    x = to_point.lon - from_point.lon
    return math.atan2(y, x)

def calculate_best_orientation(polygon=None):
    # Find which side of the polygon has the largest length
    longest_distance = 0
    best_orientation = 0
    for index in range(len(polygon.vertices)):
        vertex1 = polygon.vertices[index]
        vertex2 = polygon.vertices[(index + 1) % len(polygon.vertices)]
        if vertex1.equals(vertex2):
            continue
        distance = calculate_distance_between_points(vertex1, vertex2)
        if distance > longest_distance:
            longest_distance = distance
            best_orientation = math.atan2(vertex1.lat - vertex2.lat, vertex1.lon - vertex2.lon)

    return best_orientation

def raycast_to_polygon(origin=None, direction=None, polygon=None):
    # Define the ray as a line
    ray = Segment(origin, create_point(origin, polygon.maximum, direction))

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
    if ((q.lon <= max(p.lon, r.lon)) and (q.lon >= min(p.lon, r.lon)) and
            (q.lat <= max(p.lat, r.lat)) and (q.lat >= min(p.lat, r.lat))):
        return True
    return False

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
    # These special cases never seem to trigger
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if (o1 == 0) and onSegment(p1, p2, q1):
        print("Let Nic know about this. Colinnear case")
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if (o2 == 0) and onSegment(p1, q2, q1):
        print("Let Nic know about this. Colinnear case")
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if (o3 == 0) and onSegment(p2, p1, q2):
        print("Let Nic know about this. Colinnear case")
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if (o4 == 0) and onSegment(p2, q1, q2):
        print("Let Nic know about this. Colinnear case")
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
    orientation_vector = create_point(Coord(lat=0, lon=0), 1, direction)

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
    orientation_vector = create_point(Coord(lat=0, lon=0), 1, direction)

    point1_proj = get_projection(this_vector=point1, on_this_vector=orientation_vector)
    point2_proj = get_projection(this_vector=point2, on_this_vector=orientation_vector)
    proj_diff = abs(point1_proj - point2_proj)

    if point1_proj > point2_proj:
        point2 = create_point(point2, proj_diff, direction)
    else:
        point1 = create_point(point1, proj_diff, direction)

    return point1, point2

def calculate_furthest_point(point1=None, point2=None, direction=None):
    orientation_vector = create_point(Coord(lat=0, lon=0), 1, direction)

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
    # https://math.stackexchange.com/questions/797828/calculate-center-of-circle-tangent-to-two-lines-in-space
    angle_between = angle_between_points(previous_waypoint, current_waypoint, next_waypoint)
    bisector_angle = calculate_bisection_angle(previous_waypoint, current_waypoint, next_waypoint)
    centre_radius = radius / math.sin(angle_between / 2)

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

        circle_centres = (Coord(lon=(current_waypoint.lon + next_waypoint.lon) / 2, lat=(current_waypoint.lat + next_waypoint.lat) / 2), None)

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
    centre_of_waypoints = Coord(lon=(current_waypoint.lon + next_waypoint.lon) / 2, lat=(current_waypoint.lat + next_waypoint.lat) / 2)
    distance_forwards = math.sqrt(4 * turn_radius ** 2 - (turn_radius + layer_distance / 2) ** 2)

    centre_x = centre_of_waypoints.lon + distance_forwards * math.cos(current_direction)
    centre_y = centre_of_waypoints.lat + distance_forwards * math.sin(current_direction)

    middle_centre = Coord(lon=centre_x, lat=centre_y)
    circle_centres = ([current_waypoint_centre, middle_centre, next_waypoint_centre], None)
    return circle_centres

def calculate_single_centre_point(previous_waypoint=None, current_waypoint=None, next_waypoint=None, radius=None):
    angle_between = angle_between_points(previous_waypoint, current_waypoint, next_waypoint)
    bisector_angle = calculate_bisection_angle(previous_waypoint, current_waypoint, next_waypoint)
    centre_radius = radius / math.sin(angle_between / 2)

    centre_point = create_point(current_waypoint, centre_radius, bisector_angle)
    return centre_point

def fast_round(number, precision):
    return int(number * precision + 0.5) / precision

def on_same_axis(point1=None, point2=None, orientation=None):
    angle_from_points = math.atan2(point1.lat - point2.lat, point1.lon - point2.lon)

    if fast_round(angle_from_points, 10) == fast_round(orientation, 10) or fast_round(clamp_angle(angle_from_points + pi), 10) == fast_round(orientation, 10):
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
        new_waypoint = Waypoint(point.lon, point.lat)
        waypoints.append(new_waypoint)
    return waypoints

def calculate_closest_point_on_segment_to_point(segment_start=None, segment_end=None, reference_point=None):
    segment_vector = Coord(lon=segment_end.lon - segment_start.lon, lat=segment_end.lat - segment_start.lat)
    segment_to_reference = Coord(lon=reference_point.lon - segment_start.lon, lat=reference_point.lat - segment_start.lat)
    percentage_along_segment = (segment_to_reference.lon * segment_vector.lon + segment_to_reference.lat * segment_vector.lat) / (segment_vector.lon ** 2 + segment_vector.lat ** 2)
    percentage_along_segment = max(0, min(percentage_along_segment, 1))
    closest_point = Coord(lon=segment_start.lon + percentage_along_segment * segment_vector.lon, lat=segment_start.lat + percentage_along_segment * segment_vector.lat)
    return closest_point

def clamp_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))

def calculate_closest_perpendicular_vertex(polygon=None, orientation=None, start_point=None):
    perpendicular_direction = Coord(lon=math.sin(orientation), lat=- math.cos(orientation))
    furthest_vertices = [0, 0]
    furthest_projections = [0, 0]
    vertex_count = 0
    for vertex in polygon.vertices:
        starting_to_vertex = Coord(lon=vertex.lon - start_point.lon, lat=vertex.lat - start_point.lat)
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

    path_start = create_point(centre_vertex, distance, bisection_angle)
    return path_start

def angle_between_points(pointA=None, pointB=None, pointC=None):
    AB = Coord(lon=pointB.lon - pointA.lon, lat=pointB.lat - pointA.lat)
    BC = Coord(lon=pointC.lon - pointB.lon, lat=pointC.lat - pointB.lat)
    if AB.dot(BC) / (AB.magnitude() * BC.magnitude()) > 1 or AB.dot(BC) / (AB.magnitude() * BC.magnitude()) < -1:
        angle = pi
        return angle

    angle = math.acos(AB.dot(BC) / (AB.magnitude() * BC.magnitude()))
    return angle + pi

def calculate_bisection_angle(point_A=None, point_B=None, point_C=None, acute=True):
    angle_to_A = math.atan2(point_A.lat - point_B.lat, point_A.lon - point_B.lon)
    angle_to_C = math.atan2(point_C.lat - point_B.lat, point_C.lon - point_B.lon)
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
    forward_direction = create_point(Coord(lon=0, lat=0), 1, orientation)
    reference_point = Coord(lon=distant_point.lon - origin.lon, lat=distant_point.lat - origin.lat)

    projection = get_projection(this_vector=reference_point, on_this_vector=forward_direction)
    if projection <= 0:
        return None

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
    return Coord(lon=point.lon + dist * math.cos(angle), lat=point.lat + dist * math.sin(angle))

def find_segment_intersection(segment1, segment2):
    xdiff = Coord(lon=segment1.start.lon - segment1.end.lon, lat=segment2.start.lon - segment2.end.lon)
    ydiff = Coord(lon=segment1.start.lat - segment1.end.lat, lat=segment2.start.lat - segment2.end.lat)

    def det(a, b):
        return a.lon * b.lat - a.lat * b.lon

    div = det(xdiff, ydiff)
    if div == 0:
        return None

    d = Coord(lon=det(segment1.start, segment1.end), lat=det(segment2.start, segment2.end))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return Coord(lon=x, lat=y)

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

    origin = Coord(lon=x_diff, lat=y_diff)
    for index in range(vertex_count):
        angle = angle_percentages[index] * 2*pi
        vertex = create_point(origin, max_dist, angle)
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

    random_start = Coord(lon=random.uniform(x_diff - abs(x_diff) / 2, x_diff + abs(x_diff) / 2), lat=random.uniform(y_diff - abs(y_diff) / 2, y_diff + abs(y_diff) / 2))
    return random_start

def calculate_distance_between_points(point_1=None, point_2=None):
    return math.sqrt((point_1.lon - point_2.lon) ** 2 + (point_1.lat - point_2.lat) ** 2)

def print_waypoints(waypoints=None):
    for index, waypoint in enumerate(waypoints):
        print(index, " | ", waypoint.lon, waypoint.lat)

def earth_radius(latitude):
    # Constants for the WGS-84 ellipsoid (Earth)
    a = 6378137  # Semi-major axis in metres
    b = 6356752.314245  # Semi-minor axis in metres

    # Calculate the radius at the given latitude using the formula
    numerator = (a ** 2 * math.cos(latitude)) ** 2 + (b ** 2 * math.sin(latitude)) ** 2
    denominator = (a * math.cos(latitude)) ** 2 + (b * math.sin(latitude)) ** 2
    radius = math.sqrt(numerator / denominator)

    return radius

def do_entire_simulation(do_plot=True, do_random=True):
    if do_random:
        search_area_polygon = create_random_search_area(7)
        layer_distance = create_random_layer_distance([0.5, 5])
        start_point = create_random_start_point()
        minimum_turn_radius = random.uniform(0.1, 5)
        curve_resolution = 5
    else:
        start_point = Coord(lat=-38.40, lon=144.88)
        search_area_waypoints = [Coord(lat=-38.383944, lon=144.880181), Coord(lat=-38.397322, lon=144.908826), Coord(lat=-38.366840, lon=144.907242), Coord(lat=-38.364585, lon=144.880813)]
        search_area_polygon = Polygon(search_area_waypoints)
        layer_distance = 400  # Metres
        minimum_turn_radius = 150  # Metres
        curve_resolution = 0.01  # Waypoints per metre on turns
        scaling_factor = 111320 / math.cos(search_area_polygon.centroid.lat)
        layer_distance /= scaling_factor
        minimum_turn_radius /= scaling_factor
        curve_resolution *= scaling_factor

    sensor_size = (12.8, 9.6)
    focal_length = 16
    paint_overlap = 0.1
    angle = None

    path_generator = SearchPathGenerator()
    path_generator.set_data(search_area=search_area_polygon)
    path_generator.set_parameters(alt=200, orientation=angle, paint_overlap=paint_overlap, focal_length=None, sensor_size=None, minimum_turn_radius=minimum_turn_radius, layer_distance=layer_distance, curve_resolution=curve_resolution, start_point=start_point)

    error = path_generator.generate_search_area_path(do_plot=do_plot)
    print(error)
    return path_generator.error

def run_number_of_sims(count=None, plot=None, do_random=False):
    error_count = 0
    for index in range(count):
        if index % math.ceil(count / 10) == 0:
            print("Progress:", index / count * 100, "% |", index, "/", count)
        error = do_entire_simulation(do_plot=plot, do_random=do_random)
        if error:
            error_count += 1

    print("Simulation Complete | Error count:", error_count, "/", count, "| Error percentage:", error_count / count * 100, "%")

def main_function():
    print("You are running a test of the search area path generation. If any runtime errors occur please tell Nic in mission management thank you.")
    run_number_of_sims(1, plot=True, do_random=True)


if __name__ == "__main__":
    main_function()
