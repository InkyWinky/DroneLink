# Spline Generator
## What it does
This script is capable of creating a custom spline between input waypoints, then outputting an interpolated list
of waypoints to create a smooth path.

The algorithm works as follows (general gist):
1. Loop over each waypoint given by the user except the last one.
2. For each waypoint, travel in a straight line towards the next waypoint. Once the next waypoint has been reached, begin turning towards the following waypoint.
3. If turning after the waypoint results in crossing a user defined boundary, loop backwards through the completed waypoints and adjust the point along the turning circle at which the waypoint is reached.
4. Connect the final waypoint with a straight line.

## Parameters
```waypoints``` is a list of two element lists, containing the longitude and latitude coordinates of the waypoints. They must be defined in decimal degrees. Example:

```waypoints = [[34.421, 101.991], [35.633, 100.492], [37.543, 102.296]]```

```radius_range``` is a tuple of a minimum turning radius and a maximum turning radius <b>(in metres)</b> acceptable for the curves of the spline.
In the current version, only the minimum turning radius is functional and the maximum turning radius only has to be larger for the SplineGenerator class to operate. Example:

```radius_range = (34.592, 35)```

```radius_units_metres``` is a boolean showing whether the ```radius_range``` is in metres or not. In the current version, only input metres.

```boundary_points``` is a list of two elements lists, containing the longitude and latitude coordinates of a bounding polygon. The values must be expressed in decimal degrees.

```boundary_resolution``` represents how many equally spaces step checks will be performed when a boundary collision is detected.
The higher this parameter, the closer to the minimum boundary tolerance the spline will generate. 100 is a good default here.

```tolerance``` is the minimum distance <b>(in metres)</b> the spline is allowed to generate from the boundary polygon. A tolerance of zero will allow the spline to generate on the bounding box.

```curve_resolution``` is the number of waypoints per metre, the spline generator will interpolate curves to.
## How to use
The SplineGenerator class is easy to use. Follow these steps.
1. Import the class file.
```
import SplineGenerator as spline
```
2. Define arguments.
```
waypoints = [[0, 1], [2, 5], [6, 7.5]]
radius_range = (43, 44)
radius_units_metres = True
boundary_points = [[0,0], [0, 10], [9, 10], [10, 0]]
boundary_resolution = 100
tolerance = 2.4
curve_resolution = 2
```
3. Instantiate an instance of the class. Example:
```
spliner = spline.SplineGenerator(waypoints, radius_range, radius_units_metres, boundary_points, boundary_resolution, tolerance, curve_resolution)
```
Upon initialisation of the SplineGenerator class, the spline will automatically be calculated.
4. Retrieve the interpolated and smooth points of the spline.

<b>Retrieve in dictionary format</b>
```
waypoints_dictionary = spliner.get_waypoint_in_dictionary()
```
<b>Plot waypoints</b>
```
spliner.plot_waypoints(show_points=True, show_original=True, show_centres=True, show_boundary=True, save_fig=False, count=None)
```
<b>Read custom waypoint data directly</b>
```
custom_waypoints = spliner.waypoints
```
## Editing Waypoints Dynamically
Once the spline has generated, waypoints can be reordered, added, or removed without having to instantiate another instance of
the class.

<b>Adding waypoints</b>
```
spliner.add_waypoint(new_waypoint, index)
```

<b>Removing waypoints</b>
```
spliner.remove_waypoint(index)
```

<b>Reorder waypoints</b>
```
spliner.reorder_waypoint(first_index, second_index, swap_flag)
```
The swap flag determines if the elements at the first index and second index should swap.

## Capabilities
+ Custom interpolation resolution
+ Obeys minimum turning radius

## Not Implemented / Drawbacks
+ Doesn't handle waypoints where the distance between them is less than twice the minimum turning radius.