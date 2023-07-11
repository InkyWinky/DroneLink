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
        self.entrance = None  # Point instance for where the Albatross starts turning
        self.exit = None  # Point instance for where the Albatross stops turning
        self.turn_direction = None  # "clockwise" or "counter_clockwise"
        self.curve_waypoints = None  # List of Point instances that are the interpolated points of the curve


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
    minimum_turn_radius = None  # The minimum turning radius of the plane at cruise speed in metres
    boundary_resolution = None  # A factor inversely proportional to the step size that the path will adjust to avoid the boundary
    boundary_tolerance = None  # The minimum distance from the boundary the path must remain
    orientation = None  # Desired axis of orientation set by the user or calculated as the most efficient
    curve_resolution = None  # How many waypoints per metre we want
    max_flight_time = None  # The maximum amount of flight time
    sensor_size = None  # (width, height) in mm
    focal_length = None  # Lens focal length in mm
    paint_overlap = None  # Minimum paint overlap required in terms of percentage. Must be less than 100%
    paint_radius = None  # The radius in metres around the plane that the cameras can see / paint
    layer_distance = None

    error = False

    # Output Data
    path_waypoints = None  # Generated list of Waypoint class instances that make up the search path
    flight_time = None  # Calculated (estimate) flight time for the given path

    def set_data(self, raw_waypoints=None, search_area=None, boundary=None):
        if raw_waypoints is not None:
            self.raw_waypoints = raw_waypoints
        if search_area is not None:
            self.search_area = search_area
        if boundary is not None:
            self.boundary = boundary

    def set_parameters(self, minimum_turn_radius=None, boundary_resolution=None, layer_distance=None, boundary_tolerance=None, curve_resolution=None, orientation=None, start_point=None, focal_length=None, sensor_size=None, paint_overlap=None):
        if minimum_turn_radius is not None:
            self.minimum_turn_radius = minimum_turn_radius
        if boundary_resolution is not None:
            self.boundary_resolution = boundary_resolution
        if boundary_tolerance is not None:
            self.boundary_tolerance = boundary_tolerance
        if curve_resolution is not None:
            self.curve_resolution = curve_resolution
        if orientation is not None:
            self.orientation = orientation
        if start_point is not None:
            self.start_point = start_point
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
        self.paint_radius = calculate_viewing_radius(sensor_size=self.sensor_size, focal_length=self.focal_length, altitude=100)
        if self.layer_distance is None:
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
        smooth_points = self.smooth_rough_points()

        # Complete post-calculation data validation checks
        validation, error_message = self.do_post_validation_checks(waypoints=rough_points)
        if do_plot:
            self.print_waypoints(rough_points)
            self.plot_waypoints(waypoints=rough_points, polygon=self.search_area)
        elif validation is None:
            self.error = error_message
            self.print_debug()
            self.plot_waypoints(waypoints=rough_points, polygon=self.search_area)

    def print_debug(self):
        print("ERROR:", self.error)
        print("\tSearch Area:")
        for vertex in self.search_area.vertices:
            print("\t\t", vertex.x, vertex.y)
        print("\tStart Point:")
        print("\t\t", self.start_point.x, self.start_point.y)
        print("\tLayer Distance:")
        print("\t\t", self.layer_distance)

    def smooth_rough_points(self):
        pass

    def print_waypoints(self, waypoints=None):
        for index, waypoint in enumerate(waypoints):
            print(index, " | ", waypoint.x, waypoint.y)

    def plot_waypoints(self, waypoints=None, polygon=None, equal_axis=True):
        poly_x = []
        poly_y = []
        for point in polygon.vertices:
            poly_x.append(point.x)
            poly_y.append(point.y)
        poly_x.append(polygon.vertices[0].x)
        poly_y.append(polygon.vertices[0].y)
        plt.plot(poly_x, poly_y)

        x_vals = []
        y_vals = []
        for point in waypoints:
            x_vals.append(point.x)
            y_vals.append(point.y)
        plt.plot(x_vals, y_vals)
        plt.scatter(x_vals, y_vals)

        plt.scatter(waypoints[0].x, waypoints[0].y, color='red')
        plt.annotate("First waypoint", (waypoints[0].x, waypoints[0].y), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.scatter(self.search_area.centroid.x, self.search_area.centroid.y, color='purple')
        plt.annotate("Centre of calculations", (self.search_area.centroid.x, self.search_area.centroid.y), textcoords="offset points", xytext=(0, 10), ha='center')
        plt.scatter(self.start_point.x, self.start_point.y, marker='^', color='black')
        plt.annotate("Takeoff", (self.start_point.x, self.start_point.y), textcoords="offset points", xytext=(0, 10), ha='center')

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

        # Find which end of the path is closest to the take-off location. Make the closest one the zeroth index by reversing if necessary
        distance_start = calculate_distance_between_points(self.start_point, rough_waypoints[0])
        distance_end = calculate_distance_between_points(self.start_point, rough_waypoints[-1])
        if distance_end < distance_start:
            rough_waypoints.reverse()

        return rough_waypoints

    def generate_first_point(self):
        # Left of the orientation axis is negative and to the right is positive
        # Check if the start point is in the search area or not
        if not self.search_area.contains(self.start_point):
            # Find the closest point along the polygon from the start point
            closest_point = calculate_closest_point_on_polygon(polygon=self.search_area, start_point=self.start_point)
        else:
            closest_point = self.start_point
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
        if self.minimum_turn_radius is None or self.curve_resolution is None:
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

    # If the point is outside the search area now, bring is back in and put it near the closest vertex
    closest_vertex = find_closest_vertex_index(polygon=polygon, point=distant_point)
    distant_point = calculate_point_away_from_polygon(polygon=polygon, centre_vertex_index=closest_vertex, distance=layer_distance/2)

    # TODO: This is causing intersections fix it stoopid
    # If it is still outside, keep lowering the layer distance maximum 8 times
    count = 2
    while not polygon.contains(distant_point):
        distant_point = calculate_point_away_from_polygon(polygon=polygon, centre_vertex_index=closest_vertex, distance=layer_distance / count)
        count += 1
        if count >= 10:
            return None

    return distant_point

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

def do_entire_simulation(do_plot=True):
    search_area_polygon = create_random_search_area(7)
    layer_distance = create_random_layer_distance([0.5, 5])
    start_point = create_random_start_point()

    raw_waypoints = [[0, 0], [2, 4], [5, 2], [3, -2], [6, -2], [3, -5], [1, -4]]
    minimum_turn_radius = 0.5
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
    path_generator.set_parameters(orientation=angle, paint_overlap=paint_overlap, focal_length=focal_length, sensor_size=sensor_size, minimum_turn_radius=minimum_turn_radius, layer_distance=layer_distance, curve_resolution=curve_resolution, start_point=start_point)

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
    run_number_of_sims(100, plot=False)

    # raw_waypoints = [[0, 0], [2, 4], [5, 2], [3, -2], [6, -2], [3, -5], [1, -4]]
    # minimum_turn_radius = 0.5
    # search_area = [[11.423, 24.070], [10.304, 24.139], [19.507, -0.470], [19.660, -0.329], [21.390, 1.617], [22.139, 2.745], [23.923, 7.510]]
    # # search_area = [[0, 0], [0, 10], [10, 10], [10, 0]]
    # # search_area = [[0, 0], [-4, 4], [0, 10], [10, 8], [14, 2]]
    # curve_resolution = 4
    # start_point = Point(26.637, 23.066)
    # sensor_size = (12.8, 9.6)
    # focal_length = 16
    # paint_overlap = 0.1
    # angle = None
    # layer_distance = 4.0513
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

    # seg1 = Segment(Point(-0.513943242218, 14.5325684886), Point(1.13629308128, 10.1554913618))
    # seg2 = Segment(Point(2.78652940478, 5.77841423501), Point(4.43676572829, 1.40133710819))
    # print(do_segments_intersect(seg1, seg2))


if __name__ == "__main__":
    main_function()
