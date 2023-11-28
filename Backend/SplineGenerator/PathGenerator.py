import SplineGenerator.PointToPointPathGenerator as ptpPG
import SplineGenerator.SearchPathGenerator as saPG
import math

class PathGenerationType:
    SEARCH_AREA = "saPG"
    POINT_TO_POINT = "ptpPG"

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

    def generate_path(self):
        # Check what type of path generation is desired
        if self.path_generation_type == "saPG":  # Search area path generation
            return self.handle_saPG()

        if self.path_generation_type == "ptpPG":  # Point to point path generation
            return self.handle_ptpPG()

    def handle_saPG(self):
        # Create class instance
        path_generator = saPG.SearchPathGenerator()

        # Scale parameters
        scale_factor = 111320 / math.cos(self.search_area.centroid.lat)
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
                                      paint_overlap=self.paint_overlap)

        # Generate path
        path_generator.generate_search_area_path(do_plot=self.do_plot)

        # Return waypoints in dictionary format
        return path_generator.get_waypoints()

    def handle_ptpPG(self):
        # Scale parameters
        scale_factor = 111320 / math.cos(self.waypoints[0].coords.lat)
        scaled_turn_radius = self.minimum_turn_radius / scale_factor
        scaled_curve_resolution = self.curve_resolution * scale_factor

        # Create class instance
        path_generator = ptpPG.SplineGenerator(waypoints=self.waypoints,
                                               radius_range=(scaled_turn_radius, scaled_turn_radius + 1),
                                               boundary_points=self.boundary_points,
                                               boundary_resolution=self.boundary_resolution,
                                               tolerance=self.boundary_tolerance,
                                               curve_resolution=scaled_curve_resolution)

        # Do spline between waypoints
        path_generator.generate_spline()

        # If do_plot is True then plot the waypoints
        if self.do_plot:
            path_generator.plot_waypoints()

