from PathGenerator import *
from SearchPathGenerator import Coord, Polygon
from PointToPointPathGenerator import Waypoint


def main_function():
    # Create class instance of PathGeneration
    path_generator = PathGenerator()

    # Set the correct parameters and data

    """ For point to point path generations: """
    path_generator.path_generation_type = PathGenerationType.POINT_TO_POINT
    path_generator.minimum_turn_radius = 38  # Metres
    path_generator.curve_resolution = 0.5  # 0.5 waypoints per metre on curves
    path_generator.waypoints = [Waypoint(38.3145, -76.543),
                                Waypoint(38.315, -76.546),
                                Waypoint(38.3175, -76.548),
                                Waypoint(38.316, -76.550)]  # List of Waypoint classes with lat and lon values
    path_generator.boundary_points = [Coord(38.31729702009844, -76.55617670782419),
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
                                      Coord(38.31674255749409, -76.55294546866578)]  # List of Coord classes with lat and lon values. Optional.
    path_generator.boundary_resolution = 100  # How many checks to make when seeing alternate curve centre points. Use if boundary points is not None
    path_generator.boundary_tolerance = None  # Minimum distance the path must be from the boundary. Use if boundary points is not None

    # Optional parameters
    path_generator.do_plot = True  # If you want to plot the output

    # Call generate path and collect path points
    path_points = path_generator.generate_path()

    """ For search area path generations: """
    path_generator.take_off_point = Coord(-38.40, 144.88)  # Optional
    path_generator.path_generation_type = PathGenerationType.SEARCH_AREA
    path_generator.minimum_turn_radius = 280  # Metres
    path_generator.curve_resolution = 0.015  # 0.015 waypoints per metre on curves or 1 / 0.015 metres between each waypoint
    path_generator.search_area = Polygon([Coord(-38.383944, 144.880181), Coord(-38.397322, 144.908826), Coord(-38.366840, 144.907242), Coord(-38.364585, 144.880813)])  # Polygon Class that contains list of Coord classes with lat and lon values
    path_generator.paint_overlap = 0.1  # Fraction you want the viewing radius to overlap as the plane flies'
    path_generator.sensor_size = (12.8, 9.6)  # Size of the camera sensor in mm. Optional
    path_generator.focal_length = 16  # Focal length of the camera in mm. Use if sensor size is not None
    path_generator.layer_distance = 400  # Fixed distance between layers of the search path. Optional
    path_generator.orientation = math.pi  # Fixed axis of orientation for the search path. Optional

    # Optional parameters
    path_generator.do_plot = True  # If you want to plot the output

    # Call generate path and collect path points
    path_points = path_generator.generate_path()

    # Do as you wish with the path_points which are in the form {"lat": 0, "lon": 0, "alt": 0}


if __name__ == "__main__":
    main_function()
