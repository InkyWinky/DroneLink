import math

class Coord:
    def __init__(self, lon=None, lat=None):
        self.lon = lon  # Longitude
        self.lat = lat  # Latitude

    def magnitude(self, point=None):
        if point is None:
            return math.sqrt(self.lon ** 2 + self.lat ** 2)
        else:
            return math.sqrt(point.lon ** 2 + point.lat ** 2)

    def dot(self, point_2):
        return self.lon * point_2.lon + self.lat * point_2.lat

    def multiply(self, scalar):
        return Coord(self.lon * scalar, self.lat * scalar)

    def equals(self, point=None):
        if self.lon == point.lon and self.lat == point.lat:
            return True
        return False

class FlyToCircleTarget:

    def __init__(self):
        # Input
        self.existing_path = None  # List of Coord classes that outline the path the plane is currently on
        self.plane_location = None  # Coord of plane
        self.target_location = None
        self.turn_radius = None
        self.target_circle_radius = None
        self.minimum_distance_to_start = None

        # Intermediate
        self.start_point = None

        # Output
        self.formatted_points = None  # A returnable format for the generated spline

    def set_parameters(self):
        pass

    def set_data(self):
        pass

    def generate_path(self):
        """
        Generates a path from the current position of the plane to the closest tangent point of a circle centred at the target with desired radius.
        Returns a list of dictionary points that the plane can immediately start following.
        """
        # Initial checks

        # Create points for path
        path_points = self.generate_path_points()

        # Final checks

        # Return points in dictionary format
        return self.formatted_points

    def generate_path_points(self):
# Create points for