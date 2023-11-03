from __future__ import division, print_function
import matplotlib.pyplot as plt
import math


class SplineGenerator:
    """
    This class contains all the methods responsible for creating and modifying a custom
    spline between waypoints.
    """

    def __init__(self, waypoints=None, radius_range=None, boundary_points=None, boundary_resolution=None, tolerance=None, curve_resolution=None):
        """
        Initialiser method
            This method can be used to initialise the class with or without the parameters
            listed below.
        """
        self.waypoints = waypoints
        self.radius_range = radius_range
        self.boundary_points = boundary_points
        self.boundary_resolution = boundary_resolution
        self.tolerance = tolerance
        self.curve_resolution = curve_resolution

    def add_waypoint(self, new_waypoint=None, index=None):
        self.waypoints.insert(index, new_waypoint)
        self.generate_spline()

    def remove_waypoint(self, index=None):
        self.waypoints.pop(index)
        self.generate_spline()

    def reorder_waypoint(self, first_index=None, second_index=None, swap_flag=False):
        if swap_flag is False:
            changed_waypoint = self.waypoints.pop(second_index)
            self.waypoints.insert(first_index, changed_waypoint, )
        else:
            self.waypoints[first_index], self.waypoints[second_index] = self.waypoints[second_index], self.waypoints[first_index]
        self.generate_spline()

    def generate_spline(self):
        self.waypoints = generate_spline_including_boundary(waypoints=self.waypoints,
                                                            radius_range=self.radius_range,
                                                            boundary_points=self.boundary_points,
                                                            boundary_resolution=self.boundary_resolution,
                                                            tolerance=self.tolerance,
                                                            curve_resolution=self.curve_resolution)

    def plot_waypoints(self, show_points=True, show_original=True, show_centres=True, show_boundary=True, save_fig=False, count=None):
        x_vals = []
        y_vals = []
        if self.waypoints is not None:
            for waypoint in self.waypoints:
                if waypoint.entrance is not None:
                    x_vals.append(waypoint.entrance.lon)
                    y_vals.append(waypoint.entrance.lat)
                if waypoint.interpolated_curve is not None:
                    for point in waypoint.interpolated_curve:
                        x_vals.append(point.lon)
                        y_vals.append(point.lat)
                if waypoint.exit is not None:
                    x_vals.append(waypoint.exit.lon)
                    y_vals.append(waypoint.exit.lat)
                if waypoint.entrance is None and waypoint.exit is None:
                    x_vals.append(waypoint.coords.lon)
                    y_vals.append(waypoint.coords.lat)
            if show_points:
                plt.plot(x_vals, y_vals, '-.o', color='k', markersize=4)
            else:
                plt.plot(x_vals, y_vals, '-.o', color='k', markersize=0)

        x_orig = []
        y_orig = []
        if show_original:
            if self.waypoints is not None:
                for waypoint in self.waypoints:
                    x_orig.append(waypoint.coords.lon)
                    y_orig.append(waypoint.coords.lat)
            plt.scatter(x_orig, y_orig, color='r', s=75)

        x_cent = []
        y_cent = []
        if show_centres:
            if self.waypoints is not None:
                for waypoint in self.waypoints:
                    if waypoint.centre_point is not None:
                        x_cent.append(waypoint.centre_point.lon)
                        y_cent.append(waypoint.centre_point.lat)
                plt.scatter(x_cent, y_cent, color='b')

        if show_boundary:
            if self.boundary_points is not None:
                x_vals = [point.lon for point in self.boundary_points]
                y_vals = [point.lat for point in self.boundary_points]
                x_vals.append(self.boundary_points[0].lon)
                y_vals.append(self.boundary_points[0].lat)
                plt.plot(x_vals, y_vals, '--k')

        plt.axis('equal')
        if save_fig:
            plt.savefig('Spline' + str(count), dpi=1000)
        plt.show()


class Coord:
    def __init__(self, lon=None, lat=None):
        self.lon = lon
        self.lat = lat


class Waypoint:
    """
    A Waypoint refers to one of the original points the plane has to go through. The class has curve entrances and exits, circle centres and radius within.
    It also has a list for the interpolated points of the curve.
    """

    def __init__(self, x=None, y=None):
        self.coords = Coord(x, y)
        self.entrance = None
        self.exit = None
        self.centre_point = None
        self.radius = None
        self.interpolated_curve = None
        self.is_clockwise = None


# GENERAL USE FUNCTIONS:
# Below are some general functions the Spline class uses and ones users can use for testing or for the passing
# of individual test cases. A lot of these functions are really just specialised math functions, that allow printing.

def distance_between_two_points(point_one=Coord(), point_two=Coord()):
    """
    Gets the distance between two points.
    :param point_one: [x1, y1]
    :param point_two: [x2, y2]
    :return: Distance between two points.
    """
    distance = math.sqrt((point_one.lat - point_two.lat) ** 2 + (point_one.lon - point_two.lon) ** 2)
    return distance


def constrain_pi(theta):
    """
    Will constrain a given angle to between pi and -pi.
    :param: theta: Angle in radians to constrain.
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
    determinant = (next_waypoint.lon - previous_waypoint.lon) * (current_waypoint.lat - previous_waypoint.lat) - (
            next_waypoint.lat - previous_waypoint.lat) * (current_waypoint.lon - previous_waypoint.lon)
    determinant = round(determinant, 14)
    if determinant >= 0:
        return True
    else:
        return False


def get_closest_centre_point(previous_waypoint=Coord(), current_waypoint=Coord(), next_waypoint=Coord(), r=0.0):
    """
    Finds the centre point that is closest to the next waypoint.
    :param: previous_waypoint: [lat, lon], of the previous waypoint.
    :param: current_waypoint: [lat, lon], of the current waypoint.
    :param: next_waypoint: [lat, lon], of the next waypoint.
    :param: r: The minimum turning radius.
    :return: The [lat, lon] point of the circle centre that is closest to the next waypoint.
    """
    # Find the centre-point of the circle the path will trace.
    # Get perpendicular gradient of current waypoint to previous waypoint.
    inverse_gradient_numerator = current_waypoint.lon - previous_waypoint.lon
    inverse_gradient_denominator = current_waypoint.lat - previous_waypoint.lat
    # Angle below in reference to unit circle.
    gradient_angle = math.atan2(-inverse_gradient_numerator, inverse_gradient_denominator)
    # Get 2 possible points along that gradient from current waypoint that are of distance r.
    first_point = Coord(current_waypoint.lon + r * math.cos(gradient_angle), current_waypoint.lat + r * math.sin(gradient_angle))
    second_point = Coord(current_waypoint.lon + r * math.cos(gradient_angle + math.pi), current_waypoint.lat + r * math.sin(gradient_angle + math.pi))
    # Pick the point that is closer to the next waypoint.
    first_point_dist = math.sqrt(
        (first_point.lon - next_waypoint.lon) ** 2 + (first_point.lat - next_waypoint.lat) ** 2)
    second_point_dist = math.sqrt(
        (second_point.lon - next_waypoint.lon) ** 2 + (second_point.lat - next_waypoint.lat) ** 2)
    if first_point_dist <= second_point_dist:
        return first_point
    else:
        return second_point


def calculate_limit_lines_angle(previous_waypoint, current_waypoint, next_waypoint):
    limit_lines_angle = vertex_angle(current_waypoint, next_waypoint, previous_waypoint)
    limit_lines_angle = math.pi - limit_lines_angle
    return limit_lines_angle


def boundary_tolerance_respected(centre_point, boundary_points=None, distance=1.0):
    # If no boundary points are supplied don't worry about it
    if boundary_points is None:
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


def is_not_out_of_bounds(bounding_points=None, test_point=None):
    if bounding_points is None:
        return True
    # Solution below credit: https://stackoverflow.com/questions/217578/how-can-i-determine-whether-a-2d-point-is-within-a-polygon
    # Arrays containing the x- and y-coordinates of the polygon's vertices.
    vert_x = [point.lon for point in bounding_points]
    vert_y = [point.lat for point in bounding_points]
    # Number of vertices in the polygon
    n_vert = len(bounding_points)

    # For every candidate position within the bounding box
    test_x = test_point.lon
    test_y = test_point.lat
    c = 0
    for i in range(0, n_vert):
        j = i - 1 if i != 0 else n_vert - 1
        if (((vert_y[i] > test_y) != (vert_y[j] > test_y)) and
                (test_x < (vert_x[j] - vert_x[i]) * (test_y - vert_y[i]) / (vert_y[j] - vert_y[i]) + vert_x[i])):
            c += 1
    # If odd, that means that we are inside the polygon
    if c % 2 == 1:
        return True
    return False


def distance_point_to_segment(point, line_point1, line_point2):
    # https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    a = point.lon - line_point1.lon
    b = point.lat - line_point1.lat
    c = line_point2.lon - line_point1.lon
    d = line_point2.lat - line_point1.lat

    dot = a * c + b * d
    len_sq = c * c + d * d
    param = -1
    if len_sq != 0:
        param = dot / len_sq

    if param < 0:
        xx = line_point1.lon
        yy = line_point1.lat
    elif param > 1:
        xx = line_point2.lon
        yy = line_point2.lat
    else:
        xx = line_point1.lon + param * c
        yy = line_point2.lat + param * d

    dx = point.lon - xx
    dy = point.lat - yy

    return math.sqrt(dx ** 2 + dy ** 2)


def get_centre_point_given_percentage(previous_waypoint=Coord(), current_waypoint=Coord(), next_waypoint=Coord(), radius=1.0, percentage=0.5):
    # Calculate limit lines angle
    limit_lines_angle = calculate_limit_lines_angle(previous_waypoint, current_waypoint, next_waypoint)
    # Calculate reference angle
    initial_centre_point = get_closest_centre_point(previous_waypoint, current_waypoint, next_waypoint, radius)
    # Get direction
    direction = get_circle_direction_improved(previous_waypoint, current_waypoint, next_waypoint)
    reference_angle = math.atan2(initial_centre_point.lat - current_waypoint.lat, initial_centre_point.lon - current_waypoint.lon)
    if direction:
        angle_step = reference_angle - percentage * limit_lines_angle
    else:
        angle_step = reference_angle + percentage * limit_lines_angle
    centre_point = Coord(current_waypoint.lon + radius * math.cos(angle_step), current_waypoint.lat + radius * math.sin(angle_step))
    return centre_point


def scan_percentages_for_solution(previous_waypoint=None, current_waypoint=None, next_waypoint=None, boundary_resolution=None, boundary_points=None, radius=None, tolerance=None):
    # Loop through percentages as for loop
    centre_point_solution = None
    if boundary_points is None or boundary_resolution is None:
        return get_closest_centre_point(previous_waypoint, current_waypoint, next_waypoint, radius)
    for percentage_step in range(0, boundary_resolution + 1):
        percentage = percentage_step / boundary_resolution
        possible_point_solution = get_centre_point_given_percentage(previous_waypoint, current_waypoint, next_waypoint, radius, percentage)
        # Check the centre point is valid
        if is_not_out_of_bounds(boundary_points, possible_point_solution):
            if tolerance is None:
                distance_to_consider = radius
            else:
                distance_to_consider = radius + tolerance
            if boundary_tolerance_respected(possible_point_solution, boundary_points, distance_to_consider):
                centre_point_solution = possible_point_solution
                break
    return centre_point_solution


def get_point_from_angle(angle=0.0, origin=Coord(), radius=0.0):
    new_point = Coord(origin.lon + radius * math.cos(angle), origin.lat + radius * math.sin(angle))
    return new_point


def get_angle_from_point(origin, point):
    angle = math.atan2(point[1] - origin[1], point[0] - origin[0])
    return angle


def calculate_dual_perpendicular_angles(origin=Coord(), destination=Coord(), radius=0.0):
    distance = distance_between_two_points(origin, destination)
    if distance <= radius:
        print("ERROR: Points to find angle are closer together than the minimum turn radius. FUNCTION: calculate_dual_perpendicular_angles")
        return None, None
    destination_x_norm = destination.lon - origin.lon
    destination_y_norm = destination.lat - origin.lat
    first_angle = math.acos(radius / distance) + math.atan2(destination_y_norm, destination_x_norm)
    second_angle = - math.acos(radius / distance) + math.atan2(destination_y_norm, destination_x_norm)
    return constrain_pi(first_angle), constrain_pi(second_angle)


def calculate_entrance_and_exit(previous_point, current_waypoint, next_point, radius_range=(1.0, 3.0), boundary_points=None, boundary_resolution=10, tolerance=0.0):
    radius = radius_range[0]
    current_waypoint.radius = radius
    direction = get_circle_direction_improved(previous_point, current_waypoint.coords, next_point)
    current_waypoint.is_clockwise = direction
    current_waypoint.centre_point = scan_percentages_for_solution(previous_point, current_waypoint.coords, next_point, boundary_resolution, boundary_points, radius, tolerance)
    if current_waypoint.centre_point is None:
        # If there was no solution found, return none for both entrance and exit.
        print("=========================\n\tNO SOLUTION FOUND\n=========================")
        return None, None
    entrance_point_angle, entrance_point_angle_mirror = calculate_dual_perpendicular_angles(current_waypoint.centre_point, previous_point, radius)
    exit_point_angle, exit_point_angle_mirror = calculate_dual_perpendicular_angles(current_waypoint.centre_point, next_point, radius)
    if direction:
        entrance_point = get_point_from_angle(entrance_point_angle_mirror, current_waypoint.centre_point, radius)
        exit_point = get_point_from_angle(exit_point_angle, current_waypoint.centre_point, radius)
    else:
        entrance_point = get_point_from_angle(entrance_point_angle, current_waypoint.centre_point, radius)
        exit_point = get_point_from_angle(exit_point_angle_mirror, current_waypoint.centre_point, radius)
    return entrance_point, exit_point


def are_points_equal(point_one=None, point_two=None, rounding_error=14):
    if round(point_one.lon, rounding_error) != round(point_two.lon, rounding_error):
        return False
    if round(point_one.lat, rounding_error) != round(point_two.lat, rounding_error):
        return False
    return True


def generate_entrances_and_exits(waypoints=None, radius_range=(1.0, 3.0), boundary_points=None, boundary_resolution=10, tolerance=0.0):
    # Starting waypoint
    waypoints[0].exit = Coord(waypoints[0].coords.lon, waypoints[0].coords.lat)
    waypoints[-1].entrance = Coord(waypoints[-1].coords.lon, waypoints[-1].coords.lat)

    number_of_waypoints_to_calculate = len(waypoints) - 1
    for index in range(1, number_of_waypoints_to_calculate):
        previous_point = waypoints[index - 1].exit
        current_waypoint = waypoints[index]
        next_point = waypoints[index + 1].coords
        entrance_point, exit_point = calculate_entrance_and_exit(previous_point, current_waypoint, next_point, radius_range, boundary_points, boundary_resolution, tolerance)
        # Check to see if there wasn't a solution found
        if entrance_point is None and exit_point is None:
            return None
        current_waypoint.entrance = entrance_point
        current_waypoint.exit = exit_point
        if not are_points_equal(current_waypoint.entrance, current_waypoint.coords):
            for backwards_index in range(index - 1, 0, -1):
                backwards_previous_waypoint = waypoints[backwards_index - 1]
                backwards_current_waypoint = waypoints[backwards_index]
                backwards_next_waypoint = waypoints[backwards_index + 1]
                backwards_next_next_waypoint = waypoints[backwards_index + 2]
                radius_current = backwards_current_waypoint.radius
                radius_next = backwards_next_waypoint.radius

                if radius_current == radius_next:
                    entrance_angle = math.atan2(backwards_next_waypoint.centre_point.lat - backwards_current_waypoint.centre_point.lat, backwards_next_waypoint.centre_point.lon - backwards_current_waypoint.centre_point.lon) + math.pi / 2
                    exit_angle = math.atan2(backwards_next_waypoint.centre_point.lat - backwards_current_waypoint.centre_point.lat, backwards_next_waypoint.centre_point.lon - backwards_current_waypoint.centre_point.lon) + math.pi / 2
                else:
                    entrance_angle = math.acos(distance_between_two_points(backwards_current_waypoint.centre_point, backwards_next_waypoint.centre_point) / (radius_current - radius_next))
                    exit_angle = math.acos((radius_current + radius_next) / distance_between_two_points(backwards_current_waypoint.centre_point, backwards_next_waypoint.centre_point))

                backwards_current_waypoint.exit = get_point_from_angle(exit_angle, backwards_current_waypoint.centre_point, backwards_current_waypoint.radius)
                backwards_next_waypoint.entrance = get_point_from_angle(entrance_angle, backwards_next_waypoint.centre_point, backwards_next_waypoint.radius)
                current_dir = get_circle_direction_improved(backwards_previous_waypoint.exit, backwards_current_waypoint.coords, backwards_next_waypoint.entrance)
                next_dir = get_circle_direction_improved(backwards_current_waypoint.exit, backwards_next_waypoint.coords, backwards_next_next_waypoint.coords)

                if current_dir != next_dir:
                    # https://math.stackexchange.com/questions/1297189/calculate-tangent-points-of-two-circles
                    exit_angle, entrance_angle = get_tangency_angle(backwards_current_waypoint, backwards_next_waypoint)
                if exit_angle is None and entrance_angle is None:
                    return None
                backwards_current_waypoint.exit = get_point_from_angle(exit_angle, backwards_current_waypoint.centre_point, backwards_current_waypoint.radius)
                backwards_next_waypoint.entrance = get_point_from_angle(entrance_angle, backwards_next_waypoint.centre_point, backwards_next_waypoint.radius)

    return waypoints


def check_perpendicularity(waypoints=None, centre_points=None):
    for centre_index, waypoint_index in enumerate(range(len(waypoints) - 2, 2)):
        angle = vertex_angle(waypoints[waypoint_index], waypoints[waypoint_index + 1], centre_points[centre_index])
        if round(angle, 14) != round(math.pi / 2, 14):
            return False
        angle = vertex_angle(waypoints[waypoint_index + 2], waypoints[waypoint_index + 3], centre_points[centre_index])
        if round(angle, 14) != round(math.pi / 2, 14):
            return False
    return True


def confirm_perpendicularity(waypoints=None):
    # Check perpendicularity
    waypoints_to_check = []
    centre_points_to_check = []
    waypoints_to_check.append(waypoints[0].exit)
    for index in range(1, len(waypoints) - 1):
        waypoints_to_check.append(waypoints[index].entrance)
        waypoints_to_check.append(waypoints[index].exit)
        centre_points_to_check.append(waypoints[index].centre_point)
    waypoints_to_check.append(waypoints[-1].coords)
    return check_perpendicularity(waypoints_to_check, centre_points_to_check)


def get_arc_length(entrance_angle, exit_angle, radius, clockwise):
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
    num_of_points = math.ceil(arc_length * curve_resolution)
    return num_of_points


def interpolate_single_curve(waypoint=None, curve_resolution=3):
    waypoint_entrance_angle = math.atan2(waypoint.entrance.lat - waypoint.centre_point.lat, waypoint.entrance.lon - waypoint.centre_point.lon)
    waypoint_exit_angle = math.atan2(waypoint.exit.lat - waypoint.centre_point.lat, waypoint.exit.lon - waypoint.centre_point.lon)
    # Get the arc length between the entrance and exit
    arc_length, angle_difference = get_arc_length(waypoint_entrance_angle, waypoint_exit_angle, waypoint.radius, waypoint.is_clockwise)
    if arc_length == 0.0:
        return None
    num_of_points = get_num_of_interpolated_points(arc_length, curve_resolution)
    if waypoint_entrance_angle < 0.0:
        waypoint_entrance_angle += math.pi * 2
    if waypoint_exit_angle < 0.0:
        waypoint_exit_angle += math.pi * 2
    angle_interval = angle_difference / num_of_points
    interpolate_points = []
    for index in range(1, int(num_of_points)):
        if waypoint.is_clockwise:
            angle = waypoint_entrance_angle - index * angle_interval
        else:
            angle = waypoint_entrance_angle + index * angle_interval
        curve_point = Coord(waypoint.centre_point.lon + waypoint.radius * math.cos(angle), waypoint.centre_point.lat + waypoint.radius * math.sin(angle))
        interpolate_points.append(curve_point)
    return interpolate_points


def interpolate_all_curves(waypoints=None, curve_resolution=3):
    for waypoint in waypoints:
        # For each waypoint, check if it is the first or last waypoint then skip that as we know it's not going to be a curve
        if waypoint.centre_point is None:
            continue
        # If we have a waypoint that involves a curve, get all the points associated with that interpolation
        waypoint.interpolated_curve = interpolate_single_curve(waypoint, curve_resolution)
    return waypoints


def confirm_valid_entrance_exit_locations(waypoints=None):
    for waypoint in waypoints:
        if waypoint.centre_point is None:
            continue
        entrance_angle = math.atan2(waypoint.entrance.lat - waypoint.centre_point.lat, waypoint.entrance.lon - waypoint.centre_point.lon)
        exit_angle = math.atan2(waypoint.exit.lat - waypoint.centre_point.lat, waypoint.exit.lon - waypoint.centre_point.lon)
        waypoint_angle = math.atan2(waypoint.coords.lat - waypoint.centre_point.lat, waypoint.coords.lon - waypoint.centre_point.lon)
        clockwise = waypoint.is_clockwise
        # If the waypoint angle is not between (inclusive) the entrance and exit angle, return false.
        # TODO: Write something to return false is any of the waypoints have their coordinates outside the entrance and exit angles.

        if entrance_angle > waypoint_angle > exit_angle:
            print("Point outside the angle of entrance or exit")
            return False

        # TODO END
    return True


def ignore_duplicate_points(waypoints=None):
    for waypoint in waypoints:
        if waypoint.entrance is not None and waypoint.exit is not None:
            if are_points_equal(waypoint.entrance, waypoint.exit):
                waypoint.centre_point = None
                waypoint.entrance = None
                waypoint.exit = None
    return waypoints


def generate_spline_including_boundary(waypoints=None, radius_range=(1.0, 3.0), boundary_points=None, boundary_resolution=10, tolerance=0.0, curve_resolution=3):
    if waypoints is None:
        print("No waypoints given...")
        return None
    output_entrances_and_exits = generate_entrances_and_exits(waypoints=waypoints, radius_range=radius_range, boundary_points=boundary_points, boundary_resolution=boundary_resolution, tolerance=tolerance)
    # Check if no solution was found.
    if output_entrances_and_exits is None:
        return None
    if not confirm_perpendicularity(output_entrances_and_exits):
        print("TEST: PERPENDICULARITY BEFORE INTERPOLATION:", confirm_perpendicularity(output_entrances_and_exits))
    if not confirm_valid_entrance_exit_locations(output_entrances_and_exits):
        print("TEST: WAYPOINT WITHIN ENTRANCE AND EXIT:", confirm_valid_entrance_exit_locations(output_entrances_and_exits))
    output_duplicates_ignored = ignore_duplicate_points(output_entrances_and_exits)
    output_interpolated = interpolate_all_curves(output_duplicates_ignored, curve_resolution)
    if not confirm_perpendicularity(output_interpolated):
        print("TEST: PERPENDICULARITY AFTER INTERPOLATION:", confirm_perpendicularity(output_interpolated))
    return output_interpolated


def get_tangency_angle(waypoint_current, waypoint_next):
    radius_current = waypoint_current.radius
    radius_next = waypoint_next.radius
    distance = distance_between_two_points(waypoint_current.centre_point, waypoint_next.centre_point)
    reference_angle = math.atan2(waypoint_next.centre_point.lat - waypoint_current.centre_point.lat, waypoint_next.centre_point.lon - waypoint_current.centre_point.lon)
    # Check if circles are too close together
    if distance_between_two_points(waypoint_current.centre_point, waypoint_next.centre_point) <= waypoint_current.radius + waypoint_next.radius:
        print("====================================\n\tWAYPOINTS TOO CLOSE TOGETHER\n\tWaypoints:")
        print("\t\t", waypoint_current.coords.lon, waypoint_current.coords.lat, "\n\t\t", waypoint_next.coords.lon, waypoint_next.coords.lat)
        print("\tMinimum distance allowed:", waypoint_current.radius + waypoint_next.radius)
        print("\tCurrent distance:", distance_between_two_points(waypoint_current.centre_point, waypoint_next.centre_point), "\n====================================")
        return None, None
    # TODO Check if this is a fake solution using lots of test cases.
    if waypoint_current.is_clockwise:
        angle_exit = math.acos((radius_current + radius_next) / distance) + reference_angle
    else:
        angle_exit = math.acos((radius_current + radius_next) / distance) - reference_angle
    angle_entrance = math.pi - angle_exit
    if waypoint_current.is_clockwise:
        return angle_exit, -angle_entrance
    else:
        return -angle_exit, angle_entrance


def print_waypoints(waypoints=None):
    if waypoints is None:
        print("=============================\n\tNO WAYPOINTS TO PRINT\n=============================")
        return None
    point_count = 1
    for waypoint_index in range(len(waypoints)):
        waypoint = waypoints[waypoint_index]
        if waypoint_index == 0 or waypoint_index == len(waypoints) - 1:
            print("Point:", point_count, "|", waypoint.coords.lon, waypoint.coords.lat)
            point_count += 1
            continue
        if waypoint.entrance is not None:
            print("Point:", point_count, "|", waypoint.entrance.lon, waypoint.entrance.lat)
            point_count += 1
        if waypoint.centre_point is not None:
            for curve_point in waypoint.interpolated_curve:
                print("Point:", point_count, "|", curve_point.lon, curve_point.lat)
                point_count += 1
        else:
            print("Point:", point_count, "|", waypoint.coords.lon, waypoint.coords.lat)
            point_count += 1
        if waypoint.exit is not None:
            print("Point:", point_count, "|", waypoint.exit.lon, waypoint.exit.lat)
            point_count += 1


def generate_waypoints_from_list(waypoints=None):
    # Function that takes in a list of long and lat arrays then outputs a list of Waypoint class instances
    output_waypoints = []
    for waypoint in waypoints:
        new_waypoint = Waypoint(waypoint[0], waypoint[1])
        output_waypoints.append(new_waypoint)
    return output_waypoints


if "__main__" == __name__:
    minimum_turn_radius_feet = 125
    minimum_turn_radius_decimal_degrees = minimum_turn_radius_feet / 364567.2
    minimum_turn_radius_metres = 38.1
    minimum_turn_radius_decimal_degrees = minimum_turn_radius_metres / 111139
    waypoints_per_metre = 1
    curve_resolution = waypoints_per_metre / 0.000009009

    suas_boundary = [Coord(38.31729702009844, -76.55617670782419),
                     Coord(38.31594832826572, -76.55657341657302),
                     Coord(38.31546739500083, -76.55376201277696),
                     Coord(38.31470980862425, -76.54936361414539),
                     Coord(38.31424154692598, -76.54662761646904),
                     Coord(38.31369801280048, -76.54342380058223),
                     Coord(38.31331079191371, -76.54109648475954),
                     Coord(38.31529941346197, -76.54052104837133),
                     Coord(38.31587643291039, -76.54361305817427),
                     Coord(38.31861642463319, -76.54538594175376),
                     Coord(38.31862683616554, -76.55206138505936),
                     Coord(38.31703471119464, -76.55244787859773),
                     Coord(38.31674255749409, -76.55294546866578)]

    suas_waypoints = [Waypoint(38.3145, -76.543),
                      Waypoint(38.315, -76.546),
                      Waypoint(38.3175, -76.548),
                      Waypoint(38.316, -76.550)]

    path = SplineGenerator(waypoints=suas_waypoints,
                           radius_range=(minimum_turn_radius_decimal_degrees, minimum_turn_radius_decimal_degrees + 1),
                           boundary_points=suas_boundary,
                           boundary_resolution=100,
                           tolerance=None,
                           curve_resolution=curve_resolution)

    path.generate_spline()

    path.plot_waypoints()
    print_waypoints(path.waypoints)
