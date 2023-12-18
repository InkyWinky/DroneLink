import PointToPointPathGenerator as ptpPG
import SearchPathGenerator as saPG
import FlyToCircleTarget as ftctPG
import FlyToTargetPayload as fttpPG
import math

class PathGenerationType:
    SEARCH_AREA = "saPG"
    POINT_TO_POINT = "ptpPG"
    FLY_TO_CIRCLE_TARGET = "ftctPG"
    FLY_TO_TARGET_PAYLOAD = "fttpPG"

class PathGenerator:
    def __init__(self):
        # Type of path generation
        self.path_generation_type = None

        # Common data
        self.take_off_point = None
        self.do_plot = False

        # Common parameters
        self.minimum_turn_radius = None  # Metres
        self.curve_resolution = None  # Waypoints per metre on a curve
        self.alt = None  # Altitude to print plots at

        # Search area specific data
        self.search_area = None

        # Search area specific parameters
        self.sensor_size = None
        self.focal_length = None
        self.paint_overlap = None
        self.paint_radius = None
        self.layer_distance = None
        self.orientation = None

        # Point-to-point specific data
        self.waypoints = None
        self.boundary_points = None

        # Point-to-point specific parameters
        self.boundary_resolution = None
        self.boundary_tolerance = None

        # Target specific parameters
        self.plane_location = None
        self.plane_bearing = None
        self.target_location = None
        self.target_circle_radius = None
        self.minimum_distance_to_start = None
        self.times_to_circle = None

    def generate_path(self):
        # Check what type of path generation is desired
        if self.path_generation_type == "saPG":  # Search area path generation
            return self.handle_search_area_PG()

        if self.path_generation_type == "ptpPG":  # Point to point path generation
            return self.handle_point_to_point_PG()

        if self.path_generation_type == "ftctPG":  # Fly to circle target path generation
            return self.handle_fly_to_circle_target_PG()

        if self.path_generation_type == "fttpPG":  # Fly to target payload path generation
            return self.handle_fly_to_target_payload_PG()

    def handle_search_area_PG(self):
        # Create class instance
        path_generator = saPG.SearchPathGenerator()

        # Scale parameters
        scale_factor = 111320# / math.cos(self.search_area.centroid.lat)
        scaled_turn_radius = self.minimum_turn_radius / scale_factor
        scaled_curve_resolution = self.curve_resolution * scale_factor

        if self.layer_distance is not None:
            scaled_layer_distance = self.layer_distance / scale_factor
        else:
            scaled_layer_distance = None

        # Fill in data
        path_generator.set_data(search_area=self.search_area)

        # Fill in parameters
        path_generator.set_parameters(minimum_turn_radius=scaled_turn_radius,
                                      layer_distance=scaled_layer_distance,
                                      curve_resolution=scaled_curve_resolution,
                                      orientation=self.orientation,
                                      start_point=self.take_off_point,
                                      focal_length=self.focal_length,
                                      sensor_size=self.sensor_size,
                                      paint_overlap=self.paint_overlap,
                                      alt=self.alt)

        # Generate path
        output = path_generator.generate_search_area_path(do_plot=self.do_plot)
        if type(output) == dict:
            print(output)
            return None

        # Return waypoints in dictionary format
        return path_generator.get_waypoints()

    def handle_point_to_point_PG(self):
        # Scale parameters
        scale_factor = 111320# / math.cos(self.waypoints[0].coords.lat)
        scaled_turn_radius = self.minimum_turn_radius / scale_factor
        scaled_curve_resolution = self.curve_resolution * scale_factor

        # Create class instance
        path_generator = ptpPG.SplineGenerator(waypoints=self.waypoints,
                                               radius_range=(scaled_turn_radius, scaled_turn_radius + 1),
                                               boundary_points=self.boundary_points,
                                               boundary_resolution=self.boundary_resolution,
                                               tolerance=self.boundary_tolerance,
                                               curve_resolution=scaled_curve_resolution,
                                               alt=self.alt)

        # Do spline between waypoints
        path_generator.generate_spline()

        # If do_plot is True then plot the waypoints
        if self.do_plot:
            path_generator.plot_waypoints()

        # Get points in dict form
        return path_generator.get_waypoints()

    def handle_fly_to_circle_target_PG(self):
        # Convert bearing from north being zero degrees to positive x-axis being zero degrees
        bearing = self.plane_bearing
        updated_bearing = - bearing + math.pi / 2

        # Fill in parameters
        fly_to_target = ftctPG.FlyToCircleTarget()
        fly_to_target.set_parameters(plane_location=self.plane_location,
                                     plane_bearing=updated_bearing,
                                     target_location=self.target_location,
                                     turn_radius=self.minimum_turn_radius,
                                     target_circle_radius=self.target_circle_radius,
                                     minimum_distance_to_start=self.minimum_distance_to_start,
                                     times_to_circle=self.times_to_circle,
                                     curve_resolution=self.curve_resolution,
                                     alt=self.alt)

        path = fly_to_target.generate_path()
        path_dict = fly_to_target.get_waypoints()

        if self.do_plot:
            ftctPG.plot_waypoints(path_dict)

        return path_dict

    def handle_fly_to_target_payload_PG(self):
        path_generator = fttpPG.FlyToTargetPayload()

        # Convert bearing from north being zero degrees to positive x-axis being zero degrees
        bearing = 0
        updated_bearing = - bearing + math.pi / 2

        # Fill in parameters
        path_generator.set_parameters(plane_location=self.plane_location,
                                     plane_bearing=updated_bearing,
                                     target_location=self.target_location,
                                     turn_radius=self.minimum_turn_radius,
                                     minimum_distance_to_start=self.minimum_distance_to_start,
                                     curve_resolution=self.curve_resolution,
                                        alt=self.alt)

        path = path_generator.generate_path()
        if self.do_plot:
            fttpPG.plot_waypoints(points_dict=path, point1=path_generator.target_location)
        return path_generator.get_waypoints()