from __future__ import division, print_function
import matplotlib.pyplot as plt
import math

pi = 3.141592653589793


class Polygon:
    def __init__(self, vertices=None):
        self.vertices = vertices  # List of Point instances
        self.maximum = self.calculate_maximum_length()

    def calculate_maximum_length(self):
        max_length = 0
        for index in range(len(self.vertices)):
            length = calculate_distance_between_points(self.vertices[index], self.vertices[(index + 1) % len(self.vertices)])
            if length > max_length:
                max_length = length
        return max_length


class Waypoint:
    def __init__(self, x=None, y=None):
        self.coords = Point(x, y)  # Point instance that stores location of waypoint
        self.centre_point = None  # Point instance
        self.entrance = None  # Point instance for where the Albatross starts turning
        self.exit = None  # Point instance for where the Albatross stops turning
        self.turn_direction = None  # "clockwise" or "counter_clockwise"
        self.curve_waypoints = None  # List of Point instances that are the interpolated points of the curve


class Line:
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

    def set_parameters(self, minimum_turn_radius=None, boundary_resolution=None, boundary_tolerance=None, curve_resolution=None, orientation=None, start_point=None, focal_length=None, sensor_size=None, paint_overlap=None):
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

    def generate_path(self):
        # Pre-algorithm calculations
        self.paint_radius = calculate_viewing_radius(sensor_size=self.sensor_size, focal_length=self.focal_length, altitude=100)
        self.layer_distance = calculate_layer_distance(viewing_radius=self.paint_radius, paint_overlap=self.paint_overlap)
        self.layer_distance = 0.5

        # Complete data and parameter validation checks
        validation, error_message = self.do_validation_checks()
        if validation is None:
            print(error_message)
            return validation, error_message

        # Generate path points
        rough_points = self.generate_points()
        self.print_waypoints(rough_points)
        smooth_points = self.smooth_rough_points()
        self.plot_waypoints(waypoints=rough_points, polygon=self.search_area)

    def smooth_rough_points(self):
        pass

    def print_waypoints(self, waypoints=None):
        index = 1
        for waypoint in waypoints:
            print(index, " | ", waypoint.x, waypoint.y)

    def plot_waypoints(self, waypoints=None, polygon=None):
        x_vals = []
        y_vals = []
        for point in waypoints:
            x_vals.append(point.x)
            y_vals.append(point.y)
        plt.scatter(x_vals, y_vals)

        poly_x = []
        poly_y = []
        for point in polygon.vertices:
            poly_x.append(point.x)
            poly_y.append(point.y)
        poly_x.append(polygon.vertices[0].x)
        poly_y.append(polygon.vertices[0].y)

        plt.plot(poly_x, poly_y)
        plt.show()

    def generate_points(self):
        rough_waypoints = []
        # Generate the first point depending on where the plane starts
        first_point = self.generate_first_point()
        rough_waypoints = calculate_points_along_polygon_distanced(start_point=first_point, polygon=self.search_area, orientation=self.orientation, layer_distance=self.layer_distance)

        # rough_waypoints.append(first_point)
        # # Start loop to generate all following points until whole area is searched
        # # Raycast in direction of orientation until polygon is hit then backtrack by layer distance
        # raycast_point = raycast_to_polygon(origin=rough_waypoints[-1], direction=self.orientation, polygon=self.search_area)
        # print("First point:", rough_waypoints[-1].x, rough_waypoints[-1].y)
        # print("Raycast:", raycast_point.x, raycast_point.y)
        # distanced_point = Point(raycast_point.x + self.layer_distance * math.cos(self.orientation + pi), raycast_point.y + self.layer_distance * math.sin(self.orientation + pi))
        # rough_waypoints.append(distanced_point)
        # # Go in positive perpendicular direction by layer distance then raycast in positive direction of orientation and backtrack by layer distance
        # distant_perpendicular_point = Point(distanced_point.x + self.layer_distance * math.cos(self.orientation - pi / 2), distanced_point.y + self.layer_distance * math.sin(self.orientation - pi / 2))
        # print("Previous point:", distanced_point.x, distanced_point.y)
        # print("Distanced point:", distant_perpendicular_point.x, distant_perpendicular_point.y)
        # raycast_from_new_layer = raycast_to_polygon(origin=distant_perpendicular_point, direction=self.orientation, polygon=self.search_area)
        # distanced_raycast = Point(raycast_from_new_layer.x + self.layer_distance * math.cos(self.orientation + pi), raycast_from_new_layer.y + self.layer_distance * math.sin(self.orientation + pi))
        # rough_waypoints.append(distanced_raycast)
        # # Raycast in negative direction of orientation and backtrack by layer distance
        # negative_raycast_point = raycast_to_polygon(origin=rough_waypoints[-1], direction=self.orientation + pi, polygon=self.search_area)
        # distanced_raycast = Point(negative_raycast_point.x + self.layer_distance * math.cos(self.orientation), negative_raycast_point.y + self.layer_distance * math.sin(self.orientation))
        # rough_waypoints.append(distanced_raycast)
        # # Go in positive perpendicular direction by layer distance then raycast in negative direction of orientation and backtrack by layer distance
        # distant_perpendicular_point = Point(distanced_raycast.x + self.layer_distance * math.cos(self.orientation + pi), distanced_raycast.y + self.layer_distance * math.sin(self.orientation + pi))
        # raycast_from_new_layer = raycast_to_polygon(origin=distant_perpendicular_point, direction=self.orientation + pi, polygon=self.search_area)
        # distanced_raycast = Point(raycast_from_new_layer.x + self.layer_distance * math.cos(self.orientation), raycast_from_new_layer.y + self.layer_distance * math.sin(self.orientation))
        # # Do in both directions from start maybe
        return rough_waypoints

    def generate_first_point(self):
        # Left of the orientation axis is negative and to the right is positive
        closest_vertex, closest_vertex_index = calculate_closest_perpendicular_vertex(polygon=self.search_area, orientation=self.orientation, start_point=self.start_point)
        # Move d distance away from walls
        path_start = calculate_point_away_from_polygon(polygon=self.search_area, centre_vertex_index=closest_vertex_index, distance=self.layer_distance)
        print("Path start:", path_start.x, path_start.y)
        return path_start

    def do_validation_checks(self):
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

def raycast_to_polygon(origin=None, direction=None, polygon=None):
    # Define the ray as a line
    ray = Line(origin, Point(origin.x + polygon.maximum * math.cos(direction), origin.y + polygon.maximum * math.sin(direction)))
    # Look over each edge of polygon and check for intersection
    plt.plot([ray.start.x, ray.end.x], [ray.start.y, ray.end.y], '-.')
    for index in range(len(polygon.vertices)):
        vertex1 = polygon.vertices[index]
        vertex2 = polygon.vertices[(index + 1) % len(polygon.vertices)]

        edge = Line(vertex1, vertex2)
        if do_segments_intersect(segment1=ray, segment2=edge):
            intersection_point = find_intersection(segment1=ray, segment2=edge)
            return intersection_point

    return None

def ccw(A, B, C):
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

def do_segments_intersect(segment1=None, segment2=None):
    A = segment1.start
    B = segment1.end
    C = segment2.start
    D = segment2.end
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

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

def clamp_angle(angle, lower_bound=None, upper_bound=None):
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
    num_of_vertices = len(polygon.vertices)
    centre_vertex = polygon.vertices[centre_vertex_index]
    next_vertex_index = (centre_vertex_index + 1) % num_of_vertices
    next_vertex = polygon.vertices[next_vertex_index]
    prev_vertex_index = (centre_vertex_index + (num_of_vertices - 1)) % num_of_vertices
    prev_vertex = polygon.vertices[prev_vertex_index]
    angle_to_next = math.atan2(next_vertex.y - centre_vertex.y, next_vertex.x - centre_vertex.x)
    angle_to_prev = math.atan2(prev_vertex.y - centre_vertex.y, prev_vertex.x - centre_vertex.x)
    angle_equal_distant = (angle_to_next + angle_to_prev) / 2
    path_start = Point(centre_vertex.x + distance * math.cos(angle_equal_distant),
                       centre_vertex.y + distance * math.sin(angle_equal_distant))
    return path_start

def calculate_closest_point_on_polygon(polygon=None, start_point=None):
    # Loop over each segment of search area
    closest_point = None
    closest_distance = None
    for index in range(len(polygon.vertices)):
        segment_point_1 = polygon.vertices[index]
        segment_point_2 = polygon.vertices[(index + 1) % len(polygon.vertices)]
        # Find the closest point on segment to start location
        new_closest_point = calculate_closest_point_on_segment_to_point(segment_point_1, segment_point_2, start_point)
        new_closest_distance = calculate_distance_between_points(closest_point, start_point)
        if closest_point is None or new_closest_distance < closest_distance:
            closest_point = new_closest_point
            closest_distance = new_closest_distance
    return closest_point

def calculate_points_along_polygon_distanced(start_point=None, polygon=None, orientation=None, layer_distance=None):
    rough_waypoints = [start_point]
    count = 0
    max_points = 100
    directions = ["forward", "left"]  # 0 index is current direction to go, 1 index is previous direction travelled
    while count < max_points:
        print("Index:", count, " | ", directions[0])

        # If the current direction in direction of orientation or backwards, raycast then backtrack by layer distance
        if directions[0] == "forward":
            new_point = handle_forward_backward_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation, layer_distance=layer_distance)
        elif directions[0] == "backward":
            new_point = handle_forward_backward_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=clamp_angle(orientation + pi), layer_distance=layer_distance)
        elif directions[0] == "left":
            if directions[1] == "forward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation - pi / 2, layer_distance=layer_distance, raycast_direction=orientation)
            elif directions[1] == "backward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation - pi / 2, layer_distance=layer_distance, raycast_direction=orientation + pi)
        else:  # directions[0] == "right":
            if directions[1] == "forward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation - pi / 2, layer_distance=layer_distance, raycast_direction=orientation)
            else:  # directions[1] == "backward":
                new_point = handle_sideways_direction(origin=rough_waypoints[-1], polygon=polygon, orientation=orientation - pi / 2, layer_distance=layer_distance, raycast_direction=orientation + pi)

        if new_point is None:
            return rough_waypoints
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

def handle_forward_backward_direction(origin=None, polygon=None, orientation=None, layer_distance=None):
    raycast_point = raycast_to_polygon(origin=origin, polygon=polygon, direction=orientation)
    distant_point = create_point(raycast_point, layer_distance, orientation + pi)
    return distant_point

def handle_sideways_direction(origin=None, polygon=None, orientation=None, layer_distance=None, raycast_direction=None):
    distant_point = create_point(origin, layer_distance, orientation)
    raycast_point = raycast_to_polygon(origin=distant_point, direction=raycast_direction, polygon=polygon)
    if raycast_point is None:
        raycast_point = find_first_intersected_point(ray_origin=distant_point, ray_direction=orientation + pi, vertices=polygon.vertices)
        if raycast_point is None:
            return None
    distanced_raycast = create_point(raycast_point, layer_distance, raycast_direction + pi)
    return distanced_raycast

def create_segments_from_polygon(vertices=None):
    segments = []
    num_vertices = len(vertices)

    for i in range(num_vertices):
        start = vertices[i]
        end = vertices[(i + 1) % num_vertices]
        segment = Line(start, end)
        segments.append(segment)

    return segments

def find_first_intersected_point(ray_origin, ray_direction, vertices):
    segments = create_segments_from_polygon(vertices)

    intersected_point = None
    closest_intersection = float('inf')

    intersected = False

    for segment in segments:
        segment_start = segment.start
        segment_end = segment.end

        segment_dx = segment_end.x - segment_start.x
        segment_dy = segment_end.y - segment_start.y

        segment_length = segment_dx * segment_dx + segment_dy * segment_dy

        segment_angle = math.atan2(segment_dy, segment_dx)

        angle_diff = segment_angle - ray_direction
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        if abs(angle_diff) < math.pi / 2:
            ray_to_segment_x = segment_start.x - ray_origin.x
            ray_to_segment_y = segment_start.y - ray_origin.y

            denominator = math.sin(angle_diff) * segment_length

            if denominator != 0:
                t_ray = (ray_to_segment_x * math.sin(angle_diff) - ray_to_segment_y * math.cos(ray_direction)) / denominator
                t_segment = (ray_to_segment_x * math.sin(angle_diff) - ray_to_segment_y * math.cos(segment_angle)) / denominator

                if 0 <= t_ray <= 1 and 0 <= t_segment <= 1 and t_ray < closest_intersection:
                    closest_intersection = t_ray
                    intersected_point = Point(
                        ray_origin.x + t_ray * math.cos(ray_direction),
                        ray_origin.y + t_ray * math.sin(ray_direction)
                    )
                    intersected = True

    return intersected_point if intersected else None

def create_point(point=None, dist=None, angle=None):
    return Point(point.x + dist * math.cos(angle), point.y + dist * math.sin(angle))

def find_intersection(segment1, segment2):
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

def main_function():
    raw_waypoints = [[0, 0], [2, 4], [5, 2], [3, -2], [6, -2], [3, -5], [1, -4]]
    minimum_turn_radius = 0.5
    search_area = [[0, 0], [0, 10], [10, 10], [10, 0]]
    curve_resolution = 4
    start_point = Point(2, 9)
    sensor_size = (12.8, 9.6)
    focal_length = 16
    paint_overlap = 0.1
    angle = 0

    search_area_polygon = []
    for point in search_area:
        search_area_polygon.append(Point(point[0], point[1]))
    search_area_polygon = Polygon(search_area_polygon)

    path_generator = SearchPathGenerator()
    path_generator.set_data(search_area=search_area_polygon)
    path_generator.set_parameters(paint_overlap=paint_overlap, focal_length=focal_length, sensor_size=sensor_size, minimum_turn_radius=minimum_turn_radius, curve_resolution=curve_resolution, orientation=angle, start_point=start_point)

    path_generator.generate_path()


if __name__ == "__main__":
    main_function()
