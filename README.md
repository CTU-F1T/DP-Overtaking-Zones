# Optimization toolbox ng_trajectory

**ng_trajectory** is a toolbox for solving the optimal racing line problem using various methods and approaches. The main idea stands on using a genetic algorithm, although other approaches may be used as well.

Currently we distinguish 5 groups of algorithms:

1. **Selectors**
   Selectors take the input path and select a subset of these points.
2. **Segmentators**
   Segmentators split the track into segments using the selected point subset.
3. **Interpolators**
   Interpolators are used for interpolating the selected point subset in order to get, e.g., curvature.
4. **Optimizers**
   Optimizers take the data from the previous three parts and use them to find the optimal racing line.
5. **Criterions**
   Criterions are used for obtaining the fitness value given the waypoints.

The whole application does run multiple times:

 - variating "variate" parameter,
 - repeating "loop" times,
 - optimization "cascade".

The configuration file is using "parent-nesting" parameter handling. This means that the parameter defined on the top level is visible in lower levels (i.e., instead of specifying segmentator for each part of the cascade, it can be set on the top level).

## Minimal version of the configuration:
```json
{
    "_version": 2,
    "loops": 1,
    "groups": 20,
    "interpolator": "cubic_spline",
    "segmentator": "flood_fill",
    "selector": "uniform",
    "cascade": [
        {
            "algorithm": "matryoshka",
            "budget": 10,
            "layers": 5,
            "criterion": "profile",
            "criterion_args": {
                "overlap": 100
            }
        }
    ],
    "start_points": "start_points.npy",
    "valid_points": "valid_points.npy",
    "logging_verbosity": 2
}
```

## Available algorithms:

### Optimizers

Optimizers are main parts of the whole process. They take waypoints and run
optimization in order to find the best path possible.

_ng_trajectory.optimizers.*_

- _matryoshka_        Matryoshka transformation for track optimization (2D).
- _braghin_           Braghin's transformation method for track optimization (1D).

```html
Init (general) parameters:
budget (int) = 100 [Budget parameter for the genetic algorithm.]
groups (int) = 8 [Number of groups to segmentate the track into.]
workers (int) = os.cpu_count() [Number threads for the genetic algorithm.]
penalty (float) = 100 [Constant used for increasing the penalty criterion.]
criterion (callable) = static 0 [Function to evaluate current criterion.]
criterion_args (dict) = {} [Arguments for the criterion function.]
interpolator (callable) = return the same [Function to interpolate points.]
interpolator_args (dict) = {} [Arguments for the interpolator function.]
segmentator (callable) = each segment span over the whole track [Function to segmentate track.]
segmentator_args (dict) = {} [Arguments for the segmentator function.]
selector (callable) = first m points are selected [Function to select path points as segment centers.]
selector_args (dict) = {} [Arguments for the selector function.]
logging_verbosity (int) = 2 [Index for verbosity of the logger.]

Init (viz.) parameters:
plot (bool) = False [Whether a graphical representation should be created.]
```

#### Matryoshka
_optimizers.matryoshka_

Matryoshka transformation for track optimization (2D).

This optimizers segmentates the track into 2D sequence of segments. Each waypoint of the racing line is situated into one of these segments. Interpolating them in order yields a path.

In order to efficiently move inside the segments, a homeomorphism transformation is created (Matryoshka).

For the optimization itself, Nevergrad is used.


```html
Init (matryoshka) parameters:
hold_matryoshka (bool) = False [Whether the transformation should be created only once.]
grid (list) = computed by default [X-size and y-size of the grid used for points discretization.]
```

#### Braghin
_optimizers.braghin_

Braghin's transformation method for track optimization (1D).

This optimizer is an implementation of an approach described in [1]. The track is characterized by "cuts", a 1D lines placed on the track, where on each cut there is a single path waypoint. Since we are aware of their order, we can just simply interpolate these points to receive a path.

The optimization itself is done using Nevergrad.

[1]: F. Braghin, F. Cheli, S. Melzi, and E. Sabbioni. 2008. Race driver model. Computers & Structures 86, 13 (July 2008), 1503–1516.


```html
Init (braghin) parameters:
hold_transform (bool) = False [Whether the transformation should be created only once.]
endpoint_distance (float) = 0.2 [Starting distance from the center for creating transformation.]
endpoint_accuracy (float) = 0.02 [Accuracy of the center-endpoint distance for transformation.]
line_reduction (float) = 3 [Factor by which the number of line points is lowered before internal interpolation.]
grid (list) = computed by default [X-size and y-size of the grid used for points discretization.]
```


### Criterions

Criterions are used for calculating a fitness value during the optimization.


_ng_trajectory.criterions.*_

- _curvature_         Curvature criterion for fitness evaluation.
- _length_            Length criterion for fitness evaluation.
- _profile_           Profile criterion for fitness evaluation.


#### Curvature
_criterions.curvature_

Curvature criterion for fitness evaluation.

This criterion computes fitness value from curvature of the path. Since we expect that the input data already contain curvature, the fitness itself is computed as:

    sum( (k_i)^2 )


#### Length
_criterions.length_

Length criterion for fitness evaluation.

This criterion computes fitness value from length of the path. We calculate real segment-based length, i.e., sum of all sub-segment parts of the path.


#### Profile
_criterions.profile_

Profile criterion for fitness evaluation.

This criterion computes fitness value by simulating the vehicle over the input path. There are various parameters to be set. But mostly, we focus on a simple vehicle model and simple environment interaction by friction coefficient, air density, etc.

Note: The parameters shown below are not synced with the algorithm itself. Therefore, pay attention to any updates.


```html
Parameters:
overlap (int) = 0 [Size of the trajectory overlap. 0 disables this.]

Init parameters:
_mu (float) = 0.2 [Friction coeficient]
_g (float) = 9.81 [Gravity acceleration coeficient]
_m (float) = 3.68 [Vehicle mass]
_ro (float) = 1.2 [Air density]
_A (float) = 0.3 [Frontal reference aerodynamic area]
_cl (float) = 1 [Drag coeficient]
v_0 (float) = 0 [Initial speed [m.s^-1]]
v_lim (float) = 4.5 [Maximum forward speed [m.s^-1]]
a_acc_max (float) = 0.8 [Maximum longitudal acceleration [m.s^-2]]
a_break_max (float) = 4.5 [Maximum longitudal decceleration [m.s^-2]]
```


### Interpolators

Interpolators are used for interpolating the waypoints / path subsets in order to get full (continuous) path.

_ng_trajectory.interpolators.*_

- _cubic_spline_      Cubic spline interpolator.


#### Cubic Spline
_interpolators.cubic_spline_

Cubic spline interpolator.

This interpolator connects the racing line waypoints using cubic spline. Therefore, the resulting path is differentiable two times, and its curvature is continuous and "smooth". The curvature is computed as follows:

    K = (x' * y'' - y' * x'') / ( x'**2 + y'**2 )**(3/2)

Source: https://www.math24.net/curvature-radius/

Interpolation is done by CubicSpline from scipy.interpolate.

Note: It is expected that the input points describe a continuous path (end-start).


```html
Parameters:
int_size (int) = 400 [Number of points in the interpolation.]
```


### Segmentators

Segmentators are used for splitting the track into segments, based on the selection of their centers.

_ng_trajectory.segmentators.*_

- _euclidean_         Track segmentator based on euclidean distance from the center.
- _flood_fill_        Track segmentator based on the flood fill.


#### Euclidean
_segmentators.euclidean_

Track segmentator based on euclidean distance from the center.

This segmentator splits the track into segments based on the distance of the individual track parts from the group centers.

Note: Even though this is fast, it can missalign points (e.g., when they are behind a close wall).


```html
Parameters:
range_limit (float) = 0 [Maximum distance from the center of the segment. 0 disables this.]
```


#### Flood Fill
_segmentators.flood_fill_

Track segmentator based on the flood fill.

This segmentator splits the track into segments by flood fill algorithm from the centers.


```html
Parameters:
range_limit (float) = 0 [Maximum distance from the center of the segment. 0 disables this.]

Init parameters:
hold_map (bool) = False [When true, the map is created only once.]
```


### Selectors

Selectors are used for obtaining a subset of path's points,
which are later used for track segmentation.

_ng_trajectory.selectors.*_

- _curvature_         Points selector based on the path's shape.
- _uniform_           Uniform selector.
- _curvature_sample_  Sampling selector based on the curvature.


#### Curvature
_selectors.curvature_

Points selector based on the path's shape.

This selector obtains a subset of path points in order to segment the track more intelligently. Points are situated in turns, with some filling on the straight sections.

The algorithm works as follows:

1.  positive and negative peaks on the curvature are found and populated by cuts,
2. close cuts are merged to avoid redundancy,
3. long cut-less sections of the track are artificially filled with equidistant cuts,
4. sections of the track between two consecutive cuts where the sign of the curvature changes are filled with additional cuts, and
5. close cuts are filtered once again.

The current version segments the track automatically, given several parameters.

Note: The number of segments is determined differently:
 - -1 is selection based on dx
 - -2 is selection based on dy
 - -3 is selection based on curvature


```html
Parameters:
track_name (str) = unknown [Name of the track.]
plot (bool) = False [Whether the images are generated.]
interpolation_factor (float) = 24.0 [Factor to reduce number of points prior to the interpolation.]
peaks_height (float) = 0.0 [Minimum absolute height of peaks.]
peaks_merge (int) = 0 [Width of the area used for peaks merging.]
peaks_filling (int) = 1000000 [Width of the area for filling the points.]
```


#### Uniform
_selectors.uniform_

Uniform selector.

This selector uniformly samples the input path. It is not equidistant, but rather index-equidistant.


```html
Init parameters:
rotate (float) = 0 [Parameter for rotating the subset selection. 0 is not rotated. <0, 1)]
```


#### Curvature Sample
_selectors.curvature_sample_

Sampling selector based on the curvature.

This selector samples points of the path according to their curvature, based on [1]. Sampling is non-repetitive.

Note: This means, that the result is different everytime.

[1]: Matteo Botta, Vincenzo Gautieri, Daniele Loiacono, and Pier Luca Lanzi. 2012. Evolving the optimal racing line in a high-end racing game. In 2012 IEEE Conferenceon Computational Intelligence and Games (CIG). 108–115. ISSN: 2325-4289


```html
Parameters:
interpolation_size (int) = 100 [Number of points used for interpolation.]
```


## General parameters:

```html
_version (int) = None [Version of the configuration.]
_comment (str) = None [Commentary of the configuration file.]
cascade (list) = None [List of dicts, that is performed loops-times. Req. 'algorithm': OPTIMIZER]
start_points (str) = None [Name of the file with initial solution (i.e., centerline).]
valid_points (str) = None [Name of the file with valid positions of the track.]
```

## Optimization parameters:

```html
loops (int) = None [Number of repetitions.]
groups (int) = None [Number of segments on the track.]
variate (str) = None [Name of the field that contains multiple values. Its values are varied, run loop-cascade times.]
criterion (str) = None [Name of the function to evaluate current criterion.]
criterion_init (dict) = {} [Arguments for the init part of the criterion function.]
criterion_args (dict) = {} [Arguments for the criterion function.]
interpolator (str) = None [Name of the function to interpolate points.]
interpolator_init (dict) = {} [Arguments for the init part of the interpolator function.]
interpolator_args (dict) = {} [Arguments for the interpolator function.]
segmentator (str) = None [Name of the function to segmentate track.]
segmentator_init (dict) = {} [Arguments for the init part of the segmentator function.]
segmentator_args (dict) = {} [Arguments for the segmentator function.]
selector (str) = None [Name of the function to select path points as segment centers.]
selector_init (dict) = {} [Arguments for the init part of the selector function.]
selector_args (dict) = {} [Arguments for the selector function.]
```

## Utility parameters:

```html
logging_verbosity (int) = 1 [Index to the verbosity of used logger.]
prefix (str) = None [Prefix of the output log file. When unset, use terminal.]
plot (bool) = None [When true, images are plotted.]
plot_args (list) = None [List of dicts with information for plotter. 1 el. is used prior to the optimization, 2nd after.]
silent_stub (bool) = False [When set, the application does not report that an algorithm for some part is missing.]
```
