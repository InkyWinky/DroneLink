import unittest
import math
from SplineGenerator import *


class UnitTests(unittest.TestCase):

    def test_spline_perpendicularity(self):
        # Each test will have
        # An array of waypoint classes
        # Minimum turning radius (minimum turning radius, minimum turning radius + 1)
        # Curve resolution
        # Tolerance
        # An array of boundary points
        # Boundary resolution
        # {'waypoints': [], 'radius': 0.0, 'boundary': [], 'boundary_res': 0, 'tolerance': 0.0, 'curve_resolution': 0.0}
        # {'waypoints': [[1, 1], [2, 3], [5, 7], [7, 2], [2, -4]], 'radius': (0.9, 1.9), 'boundary': None, 'boundary_resolution': None, 'tolerance': 0.0, 'curve_resolution': 3.0}
        test_cases = [{'waypoints': [[1, 1], [2, 3], [5, 7], [7, 2], [2, -4]], 'radius': (0.9, 1.9), 'boundary': None, 'boundary_resolution': None, 'tolerance': 0.0, 'curve_resolution': 3.0},
                      {'waypoints': [[1, 1], [3, 3], [5, 5], [7, 7], [5, -4]], 'radius': (0.9, 1.9), 'boundary': None, 'boundary_resolution': None, 'tolerance': 0.0, 'curve_resolution': 1.7},
                      {'waypoints': [[1, 2], [3, 6], [5, 9], [7, 8], [5, -2]], 'radius': (0.9, 1.9), 'boundary': None, 'boundary_resolution': None, 'tolerance': 0.0, 'curve_resolution': 1.7},
                      {'waypoints': [[1, 3], [3, 2], [3, 8], [5, 4], [2, -4]], 'radius': (0.9, 1.9), 'boundary': None, 'boundary_resolution': None, 'tolerance': 0.0, 'curve_resolution': 1.7},
                      {'waypoints': [[1, 1], [1, 5], [3, 2], [5, -4], [3, 6]], 'radius': (1.9, 1.9), 'boundary': None, 'boundary_resolution': None, 'tolerance': 0.0, 'curve_resolution': 2.0}
                      ]
        for test_case in test_cases:
            waypoint_classed = [Waypoint(point[0], point[1]) for point in test_case['waypoints']]
            case = SplineGenerator(waypoints=waypoint_classed,
                                   radius_range=test_case['radius'],
                                   boundary_points=test_case['boundary'],
                                   boundary_resolution=test_case['boundary_resolution'],
                                   tolerance=test_case['tolerance'],
                                   curve_resolution=test_case['curve_resolution'])
            case.generate_spline()
            case.plot_waypoints()
            self.assertTrue(test_perpendicularity(case.waypoints))
            self.assertTrue(test_valid_entrance_exit_locations(case.waypoints))


if __name__ == '__main__':
    unittest.main()
