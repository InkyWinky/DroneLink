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
        # {'waypoints': [[1, 1], [2, 3], [5, 7], [4, 2], [2, -4]], 'radius': 0.9, 'boundary': [], 'boundary_res': 0, 'tolerance': 0.0, 'curve_resolution': 3.0}
        test_waypoint_lists = [{'waypoints': [[1, 1], [2, 3], [5, 7], [4, 2], [2, -4]], 'radius': 0.9, 'boundary': [], 'boundary_res': 0, 'tolerance': 0.0, 'curve_resolution': 3.0},
                               {},
                               {},
                               {}]
        for waypoint_list in test_waypoint_lists:
            self.assertTrue(test_perpendicularity(, len(waypoint_list)))


if __name__ == '__main__':
    unittest.main()
