import math


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def find_point_on_segment_and_distance(segment_start, segment_end, point, d):
    segment_vector = (segment_end[0] - segment_start[0], segment_end[1] - segment_start[1])
    segment_length = distance(segment_start[0], segment_start[1], segment_end[0], segment_end[1])
    unit_vector = (segment_vector[0] / segment_length, segment_vector[1] / segment_length)

    point_vector = (point[0] - segment_start[0], point[1] - segment_start[1])
    projected_distance = point_vector[0] * unit_vector[0] + point_vector[1] * unit_vector[1]
    d1 = distance(point[0], point[1], segment_start[0] + projected_distance * unit_vector[0], segment_start[1] + projected_distance * unit_vector[1])

    perpendicular_vector = (-unit_vector[1], unit_vector[0])
    displacement_vector = (perpendicular_vector[0] * d1, perpendicular_vector[1] * d1)

    desired_point = (point[0] + displacement_vector[0], point[1] + displacement_vector[1])

    return desired_point


# Example usage:
segment_start = (0, 0)
segment_end = (5, 0)
point = (3, 4)
d = 2

desired_point = find_point_on_segment_and_distance(segment_start, segment_end, point, d)
print("Desired point:", desired_point)
