from __future__ import division, print_function
import matplotlib.pyplot as plt
import math

class SplineGenerator:
    """
    This class contains all the methods responsible for creating and modifying a custom
    spline between waypoints.
    """

    def __init__(self, turn_radius=1.0, boundary_points=[], waypoints=[], curve_resolution=1.0, tolerance=0.0):
        """
        Initialiser method
            This method can be used to initialise the class with or without the parameters
            listed below.
        :param turn_radius: The minimum radius for any turn created by the spline algorithm
        in metres.
        :param boundary_points: An array of [latitude, longitude] arrays that define a
        boundary the spline path won't cross.
        :param waypoints: An array of [latitude, longitude] arrays that the spline path
        will intersect.
        :param resolution: How many waypoints per metre we want. A higher value will give a higher resolution.
        :param tolerance: How many metres within the boundary the spline generator will allow.
        """
        self._turn_radius = turn_radius
        self._boundary_points = boundary_points
        self._waypoints = waypoints
        self._curve_resolution = curve_resolution
        self._tolerance = tolerance

    def add_waypoints(self, waypoints=[]):
        """
        This method allows the adding of waypoints to the current waypoint list. They
        will be appended after all the previous waypoints.
        :param waypoints: An array of [latitude, longitude] arrays in the order the vehicle
        has to travel. As an example index 0 will be the first waypoint to go to and index
        1 the second waypoint and so on.
        """
        # Loop through each waypoint and append it to self._waypoints
        for waypoint in waypoints:
            self._waypoints.append(waypoint)

    def remove_waypoints(self, indices=[]):
        """
        This method allows users to remove waypoints by single index or multiple
        indices at a time.
        :param indices: An array of indices to remove from the waypoint list.
        [firstIndex, secondIndex, ...]
        """
        # Sort the indices array in descending order
        indices.sort(reverse=True)
        # Pop each waypoint at each index in descending order
        for index in indices:
            self._waypoints.pop(index)

    def add_boundary(self, boundary_points=[]):
        """
        This method replaces the class instance's boundary points with the list provided by the arguments.
        :param boundary_points: A list of [lat, lon] arrays that create a closed boundary. The final point can equal
        the initial point but doesn't have to. The program will connect the ends together anyway.
        """
        self._boundary_points = boundary_points

    def edit_turn_radius(self, turn_radius):
        """
        Replaces the class instance's minimum turn radius with the argument given.
        :param turn_radius: Minimum turn radius in metres.
        """
        self._turn_radius = turn_radius

    def print_waypoints(self):
        """
        Prints the current waypoints saved to the class instance.
        """
        print("Instance Waypoints:")
        if len(self._waypoints) == 0:
            print("\tNo waypoints saved.")
        for waypoint in self._waypoints:
            print("\t", waypoint, sep="")

    def generate_spline_boundary(self, print_data=False):
        pass

class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Waypoint:
    """
    A Waypoint refers to one of the original points the plane has to go through. The class has curve entrances and exits, circle centres and radius within.
    It also has a list for the interpolated points of the curve.
    """
    def __init__(self, x=0.0, y=0.0):
        self.coords = Point(x, y)
        self.entrance = None
        self.exit = None
        self.centre_point = None
        self.radius = None
        self.interpolated_curve = None
        self.is_clockwise = None

# GENERAL USE FUNCTIONS:
# Below are some general functions the Spline class uses and ones users can use for testing or for the passing
# of individual test cases. A lot of these functions are really just specialised math functions, that allow printing.

def distance_between_two_points(point_one=Point(), point_two=Point()):
    """
    Gets the distance between two points.
    :param point_one: [x1, y1]
    :param point_two: [x2, y2]
    :return: Distance between two points.
    """
    distance = math.sqrt((point_one.y - point_two.y) ** 2 + (point_one.x - point_two.x) ** 2)
    return distance

def constrain_pi(theta):
    """
    Will constrain a given angle to between pi and -pi.
    :param theta: Angle in radians to constrain.
    :return: The constrained angle in radians.
    """
    while theta < - math.pi or theta > math.pi:
        if theta < - math.pi:
            theta = theta + 2 * math.pi
        if theta > math.pi:
            theta = theta - 2 * math.pi
    return theta

def vertex_angle(point_one, point_two, point_three):
    """
    Finds the angle between three points.
    :param point_one: [x, y]
    :param point_two: [x, y]
    :param point_three: [x, y]
    :return: An angle in radians.
    """
    dist_one_two = distance_between_two_points(point_one, point_two)
    dist_one_three = distance_between_two_points(point_one, point_three)
    dist_two_three = distance_between_two_points(point_two, point_three)
    numerator = dist_one_two ** 2 + dist_one_three ** 2 - dist_two_three ** 2
    denominator = 2 * dist_one_two * dist_one_three
    inside = numerator / denominator
    if inside > 1.0:
        inside = 1
    if inside < -1.0:
        inside = -1
    angle = math.acos(inside)
    return angle

def get_circle_direction_improved(previous_waypoint, current_waypoint, next_waypoint):
    determinant = (next_waypoint.x - previous_waypoint.x) * (current_waypoint.y - previous_waypoint.y) - (
                next_waypoint.y - previous_waypoint.y) * (current_waypoint.x - previous_waypoint.x)
    determinant = round(determinant, 10)
    if determinant >= 0:
        return True
    else:
        return False

def get_closest_centre_point(previous_waypoint=Point(), current_waypoint=Point(), next_waypoint=Point(), r=0.0):
    """
    Finds the centre point that is closest to the next waypoint.
    :param previous_waypoint: [lat, lon], of the previous waypoint.
    :param current_waypoint: [lat, lon], of the current waypoint.
    :param next_waypoint: [lat, lon], of the next waypoint.
    :param r: The minimum turning radius.
    :return: The [lat, lon] point of the circle centre that is closest to the next waypoint.
    """
    # Find the centre-point of the circle the path will trace.
    # Get perpendicular gradient of current waypoint to previous waypoint.
    inverse_gradient_numerator = current_waypoint.x - previous_waypoint.x
    inverse_gradient_denominator = current_waypoint.y - previous_waypoint.y
    # Angle below in reference to unit circle.
    gradient_angle = math.atan2(-inverse_gradient_numerator, inverse_gradient_denominator)
    # Get 2 possible points along that gradient from current waypoint that are of distance r.
    first_point = Point(current_waypoint.x + r * math.cos(gradient_angle), current_waypoint.y + r * math.sin(gradient_angle))
    second_point = Point(current_waypoint.x + r * math.cos(gradient_angle + math.pi),current_waypoint.y + r * math.sin(gradient_angle + math.pi))
    # Pick the point that is closer to the next waypoint.
    first_point_dist = math.sqrt(
        (first_point.x - next_waypoint.x) ** 2 + (first_point.y - next_waypoint.y) ** 2)
    second_point_dist = math.sqrt(
        (second_point.x - next_waypoint.x) ** 2 + (second_point.y - next_waypoint.y) ** 2)
    if first_point_dist <= second_point_dist:
        return first_point
    else:
        return second_point

def calculate_limit_lines_angle(previous_waypoint, current_waypoint, next_waypoint):
    limit_lines_angle = vertex_angle(current_waypoint, next_waypoint, previous_waypoint)
    limit_lines_angle = math.pi - limit_lines_angle
    return limit_lines_angle

def boundary_tolerance_respected(centre_point, boundary_points=[], distance=1.0):
    # If no boundary points are supplied don't worry about it
    if boundary_points == []:
        return True
    # If out of bounds if the circle of radius: radius from the centre point goes out of the boundary.
    for index in range(len(boundary_points) - 1):
        distance_to_line = distance_point_to_segment(centre_point, boundary_points[index], boundary_points[index + 1])
        if distance_to_line < distance:
            return False
    # The line from the first point and last point. Connect the polygon
    distance_to_line = distance_point_to_segment(centre_point, boundary_points[-1], boundary_points[0])
    if distance_to_line < distance:
        return False
    return True

def is_not_out_of_bounds(bounding_points=[], test_point=None):
    if bounding_points == []:
        return True
    # Solution below credit: https://stackoverflow.com/questions/217578/how-can-i-determine-whether-a-2d-point-is-within-a-polygon
    # Arrays containing the x- and y-coordinates of the polygon's vertices.
    vertx = [point.x for point in bounding_points]
    verty = [point.y for point in bounding_points]
    # Number of vertices in the polygon
    nvert = len(bounding_points)

    # For every candidate position within the bounding box
    testx = test_point.x
    testy = test_point.y
    c = 0
    for i in range(0, nvert):
        j = i - 1 if i != 0 else nvert - 1
        if (((verty[i] > testy) != (verty[j] > testy)) and
                (testx < (vertx[j] - vertx[i]) * (testy - verty[i]) / (verty[j] - verty[i]) + vertx[i])):
            c += 1
    # If odd, that means that we are inside the polygon
    if c % 2 == 1:
        return True
    return False

def distance_point_to_segment(point, line_point1, line_point2):
    x_diff = line_point2.x - line_point1.x
    y_diff = line_point2.y - line_point1.y
    num = abs(y_diff * point.x - x_diff * point.y + line_point2.x * line_point1.y - line_point2.y * line_point1.x)
    den = math.sqrt(y_diff ** 2 + x_diff ** 2)
    return num / den

def get_centre_point_given_percentage(previous_waypoint=Point(), current_waypoint=Point(), next_waypoint=Point(), radius=1.0, percentage=0.5):
    # Calculate limit lines angle
    limit_lines_angle = calculate_limit_lines_angle(previous_waypoint, current_waypoint, next_waypoint)
    # Calculate reference angle
    initial_centre_point = get_closest_centre_point(previous_waypoint, current_waypoint, next_waypoint, radius)
    # Get direction
    direction = get_circle_direction_improved(previous_waypoint, current_waypoint, next_waypoint)
    reference_angle = math.atan2(initial_centre_point.y - current_waypoint.y, initial_centre_point.x - current_waypoint.x)
    if direction:
        angle_step = reference_angle - percentage * limit_lines_angle
    else:
        angle_step = reference_angle + percentage * limit_lines_angle
    centre_point = Point(current_waypoint.x + radius * math.cos(angle_step), current_waypoint.y + radius * math.sin(angle_step))
    return centre_point

def scan_percentages_for_solution(previous_waypoint=Point(), current_waypoint=Point(), next_waypoint=Point(), boundary_resolution=10, boundary_points=[], radius=1.0, tolerance=0.0):
    # Loop through percentages as for loop
    centre_point_solution = None
    for percentage_step in range(0, boundary_resolution + 1):
        percentage = percentage_step / boundary_resolution
        possible_point_solution = get_centre_point_given_percentage(previous_waypoint, current_waypoint, next_waypoint, radius, percentage)
        if is_not_out_of_bounds(boundary_points, possible_point_solution):
            if boundary_tolerance_respected(possible_point_solution, boundary_points, radius + tolerance):
                centre_point_solution = possible_point_solution
                break
    return centre_point_solution

def get_point_from_angle(angle=0.0, origin=Point(), radius=0.0):
    new_point = Point(origin.x + radius * math.cos(angle), origin.y + radius * math.sin(angle))
    return new_point

def get_angle_from_point(origin, point):
    angle = math.atan2(point[1] - origin[1], point[0] - origin[0])
    return angle

def calculate_dual_perpendicular_angles(origin=Point(), destination=Point(), radius=0.0):
    distance = distance_between_two_points(origin, destination)
    if distance <= radius:
        print("ERROR: Points to find angle are closer together than the minimum turn radius. FUNCTION: calculate_dual_perpendicular_angles")
        return None, None
    destination_x_norm = destination.x - origin.x
    destination_y_norm = destination.y - origin.y
    first_angle = math.acos(radius / distance) + math.atan2(destination_y_norm, destination_x_norm)
    second_angle = - math.acos(radius / distance) + math.atan2(destination_y_norm, destination_x_norm)
    return constrain_pi(first_angle), constrain_pi(second_angle)

def calculate_entrance_and_exit(previous_point, current_waypoint, next_point, radius_range=(1.0, 3.0), boundary_points=[], boundary_resolution=10, tolerance=0.0):
    radius = radius_range[0]
    current_waypoint.radius = radius
    direction = get_circle_direction_improved(previous_point, current_waypoint.coords, next_point)
    current_waypoint.is_clockwise = direction
    current_waypoint.centre_point = scan_percentages_for_solution(previous_point, current_waypoint.coords, next_point, boundary_resolution, boundary_points, radius)
    entrance_point_angle, entrance_point_angle_mirror = calculate_dual_perpendicular_angles(current_waypoint.centre_point, previous_point, radius)
    exit_point_angle, exit_point_angle_mirror = calculate_dual_perpendicular_angles(current_waypoint.centre_point, next_point, radius)
    if direction:
        current_waypoint.entrance = get_point_from_angle(entrance_point_angle_mirror, current_waypoint.centre_point, radius)
        current_waypoint.exit = get_point_from_angle(exit_point_angle, current_waypoint.centre_point, radius)
    else:
        current_waypoint.entrance = get_point_from_angle(entrance_point_angle, current_waypoint.centre_point, radius)
        current_waypoint.exit = get_point_from_angle(exit_point_angle_mirror, current_waypoint.centre_point, radius)

def are_points_equal(point_one=None, point_two=None, rounding_error=10):
    if round(point_one.x, rounding_error) != round(point_two.x, rounding_error):
        return False
    if round(point_one.y, rounding_error) != round(point_two.y, rounding_error):
        return False
    return True

def generate_entrances_and_exits(waypoints=[], radius_range=(1.0, 3.0), boundary_points=[], boundary_resolution=10, tolerance=0.0):
    # Starting waypoint
    waypoints[0].exit = Point(waypoints[0].coords.x, waypoints[0].coords.y)

    number_of_waypoints_to_calculate = len(waypoints) - 1
    for index in range(1, number_of_waypoints_to_calculate):
        previous_point = waypoints[index - 1].exit
        current_waypoint = waypoints[index]
        next_point = waypoints[index + 1].coords
        calculate_entrance_and_exit(previous_point, current_waypoint, next_point, radius_range, boundary_points, boundary_resolution, tolerance)
        if not are_points_equal(current_waypoint.entrance, current_waypoint.coords):
            for backwards_index in range(index - 1, 0, -1):
                backwards_previous_waypoint = waypoints[backwards_index - 1]
                backwards_current_waypoint = waypoints[backwards_index]
                backwards_next_waypoint = waypoints[backwards_index + 1]
                backwards_next_next_waypoint = waypoints[backwards_index + 2]
                radius_current = backwards_current_waypoint.radius
                radius_next = backwards_next_waypoint.radius

                if radius_current == radius_next:
                    entrance_angle = math.atan2(backwards_next_waypoint.centre_point.y - backwards_current_waypoint.centre_point.y, backwards_next_waypoint.centre_point.x - backwards_current_waypoint.centre_point.x) + math.pi / 2
                    exit_angle = math.atan2(backwards_next_waypoint.centre_point.y - backwards_current_waypoint.centre_point.y, backwards_next_waypoint.centre_point.x - backwards_current_waypoint.centre_point.x) + math.pi / 2
                else:
                    entrance_angle = math.acos(distance_between_two_points(backwards_current_waypoint.centre_point, backwards_next_waypoint.centre_point) / (radius_current - radius_next))
                    exit_angle = math.acos((radius_current + radius_next) / distance_between_two_points(backwards_current_waypoint.centre_point, backwards_next_waypoint.centre_point))
                backwards_current_waypoint.exit = Point(backwards_current_waypoint.centre_point.x + backwards_current_waypoint.radius * math.cos(exit_angle), backwards_current_waypoint.centre_point.y + backwards_current_waypoint.radius * math.sin(exit_angle))
                backwards_next_waypoint.entrance = Point(backwards_next_waypoint.centre_point.x + backwards_next_waypoint.radius * math.cos(entrance_angle), backwards_next_waypoint.centre_point.y + backwards_next_waypoint.radius * math.sin(entrance_angle))

                current_dir = get_circle_direction_improved(backwards_previous_waypoint.exit, backwards_current_waypoint.coords, backwards_next_waypoint.entrance)
                next_dir = get_circle_direction_improved(backwards_current_waypoint.exit, backwards_next_waypoint.coords, backwards_next_next_waypoint.coords)
                if current_dir != next_dir:
                    exit_angle, entrance_angle = get_tangency_angle(backwards_current_waypoint, backwards_next_waypoint)
                    backwards_current_waypoint.exit = Point(backwards_current_waypoint.centre_point.x + backwards_current_waypoint.radius * math.cos(exit_angle), backwards_current_waypoint.centre_point.y + backwards_current_waypoint.radius * math.sin(exit_angle))
                    backwards_next_waypoint.entrance = Point(backwards_next_waypoint.centre_point.x + backwards_next_waypoint.radius * math.cos(entrance_angle), backwards_next_waypoint.centre_point.y + backwards_next_waypoint.radius * math.sin(entrance_angle))

    # Connect last waypoint
    waypoints[-1].entrance = waypoints[-1].coords
    return waypoints

def plot_waypoints_v3(waypoints=None, boundary_points=None):
    x_vals = []
    y_vals = []
    for waypoint in waypoints:
        if waypoint.entrance is not None:
            x_vals.append(waypoint.entrance.x)
            y_vals.append(waypoint.entrance.y)
        if waypoint.interpolated_curve is not None:
            for point in waypoint.interpolated_curve:
                x_vals.append(point.x)
                y_vals.append(point.y)
        if waypoint.exit is not None:
            x_vals.append(waypoint.exit.x)
            y_vals.append(waypoint.exit.y)
    plt.plot(x_vals, y_vals, '-.o', color='k')

    x_orig = []
    y_orig = []
    if waypoints is not None:
        for waypoint in waypoints:
            x_orig.append(waypoint.coords.x)
            y_orig.append(waypoint.coords.y)
    plt.scatter(x_orig, y_orig, color='g')

    if waypoints is not None:
        for waypoint in waypoints:
            if waypoint.centre_point is not None:
                x_vals.append(waypoint.centre_point.x)
                y_vals.append(waypoint.centre_point.y)
    plt.scatter(x_vals, y_vals, color='b')

    if boundary_points is not None:
        x_vals = [point.x for point in boundary_points]
        y_vals = [point.y for point in boundary_points]
        x_vals.append(boundary_points[0].x)
        y_vals.append(boundary_points[0].y)
        plt.plot(x_vals, y_vals, '--k')

    plt.axis('equal')
    plt.show()

def check_perpendicularity(waypoints=[], centre_points=[]):
    for centre_index, waypoint_index in enumerate(range(1, len(waypoints) - 2, 2)):
        angle = vertex_angle(waypoints[waypoint_index], waypoints[waypoint_index - 1], centre_points[centre_index])
        if round(angle, 10) != round(math.pi / 2, 10):
            return False
        angle = vertex_angle(waypoints[waypoint_index + 1], waypoints[waypoint_index + 2], centre_points[centre_index])
        if round(angle, 10) != round(math.pi / 2, 10):
            return False
    return True

def test_perpendicularity(waypoints=[]):
    # Check perpendicularity
    waypoints_to_check = []
    centre_points_to_check = []
    waypoints_to_check.append(waypoints[0].exit)
    for index in range(1, len(waypoints)):
        waypoints_to_check.append(waypoints[index].entrance)
        waypoints_to_check.append(waypoints[index].exit)
        centre_points_to_check.append(waypoints[index].centre_point)
    return check_perpendicularity(waypoints_to_check, centre_points_to_check)

def get_arc_length(entrance_angle, exit_angle, centre_point, radius, clockwise):
    # Get the angle difference
    if clockwise:
        angle_difference = entrance_angle - exit_angle
    else:
        angle_difference = exit_angle - entrance_angle
    if angle_difference < 0.0:
        angle_difference += 2 * math.pi
    arc_length = (angle_difference / (2 * math.pi)) * (2 * math.pi * radius)
    return arc_length, angle_difference

def get_num_of_interpolated_points(arc_length=0.0, curve_resolution=3):
    num_of_points = math.floor(arc_length * curve_resolution)
    return num_of_points

def interpolate_single_curve(waypoint=None, curve_resolution=3):
    waypoint_entrance_angle = math.atan2(waypoint.entrance.y - waypoint.centre_point.y, waypoint.entrance.x - waypoint.centre_point.x)
    waypoint_exit_angle = math.atan2(waypoint.exit.y - waypoint.centre_point.y, waypoint.exit.x - waypoint.centre_point.x)
    # Get the arc length between the entrance and exit
    arc_length, angle_difference = get_arc_length(waypoint_entrance_angle, waypoint_exit_angle, waypoint.centre_point, waypoint.radius, waypoint.is_clockwise)
    num_of_points = get_num_of_interpolated_points(arc_length, curve_resolution)
    if waypoint_entrance_angle < 0.0:
        waypoint_entrance_angle += math.pi * 2
    if waypoint_exit_angle < 0.0:
        waypoint_exit_angle += math.pi * 2
    angle_interval = angle_difference / num_of_points
    interpolate_points = []
    for index in range(int(num_of_points)):
        if waypoint.is_clockwise:
            angle = waypoint_entrance_angle - index * angle_interval
        else:
            angle = waypoint_entrance_angle + index * angle_interval
        curve_point = Point(waypoint.centre_point.x + waypoint.radius * math.cos(angle), waypoint.centre_point.y + waypoint.radius * math.sin(angle))
        interpolate_points.append(curve_point)
    return interpolate_points

def interpolate_all_curves(waypoints=[], curve_resolution=3):
    for waypoint in waypoints:
        # For each waypoint, check if it is the first or last waypoint then skip that as we know its not going to be a curve
        if waypoint.centre_point is None:
            continue
        # If we have an waypoint that involves a curve, get all the points associated with that interpolation
        waypoint.interpolated_curve = interpolate_single_curve(waypoint, curve_resolution)
    return waypoints

def test_valid_entrance_exit_locations(waypoints=[]):
    for waypoint in waypoints:
        if waypoint.centre_point is None:
            continue
        entrance_angle = math.atan2(waypoint.entrance.y - waypoint.centre_point.y, waypoint.entrance.x - waypoint.centre_point.x)
        exit_angle = math.atan2(waypoint.exit.y - waypoint.centre_point.y, waypoint.exit.x - waypoint.centre_point.x)
        waypoint_angle = math.atan2(waypoint.coords.y - waypoint.centre_point.y, waypoint.coords.x - waypoint.centre_point.x)
        clockwise = waypoint.is_clockwise
        # If the waypoint angle is not between (inclusive) the entrance and exit angle, return false.
        # TODO: Write something to return false is any of the waypoints have their coordinates outside the entrance and exit angles.

        # TODO END
    return True

def generate_spline_including_boundary(waypoints=[], radius_range=(1.0, 3.0), boundary_points=[], boundary_resolution=10, tolerance=0.0, curve_resolution=3):
    output = generate_entrances_and_exits(waypoints=waypoints, radius_range=radius_range, boundary_points=boundary_points, boundary_resolution=boundary_resolution, tolerance=tolerance)
    print("TEST: PERPENDICULARITY:", test_perpendicularity(output))
    print("TEST: WAYPOINT WITHIN ENTRANCE AND EXIT:", test_valid_entrance_exit_locations(output))
    output = interpolate_all_curves(output, curve_resolution)
    return output

def check_if_solution_points_valid(entrance_point, exit_point, current_waypoint, direction, centre_point):
    pass

def get_tangency_angle(waypoint_current, waypoint_next):
    radius_current = waypoint_current.radius
    radius_next = waypoint_next.radius
    distance = distance_between_two_points(waypoint_current.centre_point, waypoint_next.centre_point)
    reference_angle = math.atan2(waypoint_next.centre_point.y - waypoint_current.centre_point.y, waypoint_next.centre_point.x - waypoint_current.centre_point.x)
    angle_exit = math.acos((radius_current + radius_next) / distance) - reference_angle
    angle_entrance = math.pi - angle_exit
    print("get_tangency_angle:", angle_exit, angle_entrance)
    # TODO Check if this is a fake solution using lots of test cases.
    if waypoint_current.centre_point.y >= waypoint_next.centre_point.y:
        return angle_exit, -angle_entrance
    else:
        return -angle_exit, angle_entrance


if "__main__" == __name__:
    """
    Below is an example to show how to use the Spline Generator class.
    First define waypoints as a list of points.
    """
    # waypoints = [[4.0, 5.0], [7.0, 6.0], [6.0, 9.0], [4.0, 7.0], [2.0, 6], [1, 3], [-3, 0], [-4, 5]]
    # waypoints = [[40, 40], [40, 70], [70, 70], [70, 40]]
    # waypoints = [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0], [5.0, 5.0], [8, 5], [9, 3], [6, -4]]
    # waypoints = [[-10, 0], [-7, 0], [-5, 0], [-3, 0], [1, 2], [5, 4], [3, 0], [5, 2], [7, 0], [9, 2], [11, 0]]
    # waypoints = [[5, 10], [9, 19], [12, 14], [11, 5], [3, -4], [-4, 2]]
    # waypoints = [[5, 2], [10, 9], [13, 6]]
    # waypoints = [[2, 4], [2, 10], [5, 10], [5, 4], [8, 4], [8, 10], [11, 10], [11, 4], [14, 4], [14, 10]]
    # waypoints = [[-0.5, 0.5], [0, 2], [2, 2], [3, 0.5], [1, 1.4], [-0.25, 0.5]]

    global_waypoints = [Waypoint(1, 3.0), Waypoint(4.0, 3), Waypoint(5.0, 5.0), Waypoint(8.0, 5.0), Waypoint(9.0, 3.0), Waypoint(6.0, -1.0)]
    # global_waypoints = [Waypoint(1, -2), Waypoint(-3, -2), Waypoint(-3, 5), Waypoint(4, 6), Waypoint(3, -6), Waypoint(-2, -6)]

    global_radius = 0.8
    right_wall = 10
    top_wall = 5.9
    bottom_wall = -1.5
    left_wall = 0

    # global_radius = 1.5
    # right_wall = 4.1
    # top_wall = 7
    # bottom_wall = -6.09
    # left_wall = -5
    global_boundary_points = [Point(left_wall, bottom_wall), Point(left_wall, top_wall), Point(right_wall, top_wall), Point(right_wall, bottom_wall)]
    output = generate_spline_including_boundary(waypoints=global_waypoints, radius_range=(global_radius, 3.0), boundary_points=global_boundary_points, boundary_resolution=100, tolerance=0, curve_resolution=3)

    plot_waypoints_v3(waypoints=global_waypoints, boundary_points=global_boundary_points)
