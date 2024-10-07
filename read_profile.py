from math import acos, cos, pi, sin
import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.stats import linregress
import argparse
parser = argparse.ArgumentParser(prog='python3 read_profile.py',
    description='''Gives a step-by-step guide to simulate the elevation of a route (saved using GPX) on a treadmill!
This was designed to allow fellow runners to better represent racing conditions during their training :D''')

parser.add_argument("-f", "--filename", help="GPX file to analyze.")
parser.add_argument("-u", "--unit", help="Whether to use kilometers or miles. Default miles.", choices=["mi", "km"], default="mi")
parser.add_argument("-ng", "--no-graph", help="Disable graph of elevation profile or not.", action='store_true')
parser.add_argument("-m", "--min-incline", help="Minimum incline permitted. Default value 0.", type=int, default=0)
parser.add_argument("-n", "--num-steps", help="Maximum number of steps. If not specified, no upper bound.", type=int, default=float("inf"))
parser.add_argument("-p", "--percent-combine", help="Percentage similarity in incline two steps must be for them to be combined. Default 2%%.", type=float, default=2)
parser.add_argument("-s", "--step-print", help="Whether or not to use alternative output format (designed more for quickly reading on treadmill).", action='store_true')


# parser.add_argument("-s", "--summarize", help=".", choices=["mi", "km"], default="mi")

args = parser.parse_args()

max_steps = args.num_steps

# Parsing an existing file:
# -------------------------

gpx_file = open(args.filename, 'r')

gpx = gpxpy.parse(gpx_file)

# Get a list of elevation points + figure out mapping
elevation_points = []
elevation_distance = []
distances = [0]

def rad (x):
    return x*pi/180

def distance (pt1, pt2):
    [Lat1, Lon1] = pt1
    [Lat2, Lon2] = pt2
    return acos((sin(rad(Lat1)) * sin(rad(Lat2))) + (cos(rad(Lat1)) * cos(rad(Lat2))) * (cos(rad(Lon2) - rad(Lon1)))) * 6371

total_dis = 0
for track in gpx.tracks:
    for segment in track.segments:
        i = 0
        for point in segment.points:
            elevation_points.append(point.elevation)
            elevation_distance.append([point.latitude, point.longitude])
            if i > 0:
                total_dis += distance(elevation_distance[i - 1], elevation_distance[i]) * 1000
                distances.append(total_dis)
            i += 1

# Now figure out the grade between each point
grades = []
elevation = []
total_distance = 0
def calculate_slope(pts):
    grade_list = []
    total_distance = 0
    for i in range(1, len(pts)):
        # Get distance between each point
        dis = distance(elevation_distance[i - 1], elevation_distance[i]) * 1000
        total_distance += dis
        grade = 100*(elevation_points[i] - elevation_points[i - 1]) / dis
        grade_list.append([grade, dis])
        print(f"Pt {i}\n\tGrade: {grade}%")
    return grade_list

# Updated clustering logic with magnitude sensitivity
def summarize_trend(distance_list, grade_list, window_size=51, poly_order=1):

    """
    Simplifies the trend of the grade list by applying smoothing using Savitzky-Golay filter.
    This will reduce fluctuations and retain the overall trend.
    Args:
        grade_list (list): List of % grades or elevations.
        window_size (int): Window size for smoothing (should be odd).
        poly_order (int): Polynomial order for the Savitzky-Golay filter.    
    Returns:
        list: Smoothed grades representing the overall trend.
    """

    # Apply Savitzky-Golay filter for smoothing
    plot = savgol_filter(grade_list, window_size, poly_order)
    slopes = []
    distances = []
    for i in range (0, len(grade_list) - window_size, window_size):
        # scipy.signal.savgol_coeffs(window_size, poly_order, deriv=1, use="dot").dot(grade_list[i:i+window_size])
        slope, intercept, r, p, se = linregress(distance_list[i:i + window_size], grade_list[i:i+window_size])
        dis = distance_list[i + window_size] - distance_list[i]
        slopes.append(slope*100)
        distances.append(dis)
    return plot, [distances, slopes]

def to_miles (m):
    return m / 1609

def generate_treadmill_steps(distances, slopes, window_size=21):
    total_distance = 0
    """
    Generate a step-by-step simulation for treadmill settings based on the smoothed grade list.
    Each step corresponds to a section of the route and is associated with a treadmill incline setting.
    
    Args:
        grade_list (list): Smoothed list of grades or elevations.
        distance_per_step (float): Horizontal distance corresponding to each step (default is 0.1 km).
    
    Returns:
        list of dicts: Each dict contains the incline and distance for that step.
    """
    treadmill_steps = []
    
    for i, (distance, incline_percentage) in enumerate(zip(distances, slopes)):
        treadmill_steps.append({
            'step': i + 1,
            'incline': max(round(incline_percentage / 0.5) * 0.5, args.min_incline),
            'distance': to_miles(distance) if args.unit == "mi" else distance / 1000,
            'cumulative_distance': to_miles(total_distance) if args.unit == "mi" else total_distance / 1000
        })
        total_distance += distance
    
    return treadmill_steps

# Apply summarization to smooth the trend
window_size = round(len(distances) / max_steps) if max_steps != float("inf") else 21
smoothed_grades, [distances, slopes] = summarize_trend(distances, elevation_points, window_size=window_size)

# Generate treadmill simulation steps based on the smoothed trend
treadmill_steps = generate_treadmill_steps(distances, slopes)

def print_steps(steps):
    final_dis = 0
    for i, step in enumerate(steps):
        up_down = "Hill" if step['incline'] > 1 else "Downhill" if step['incline'] < -1 else "Flat"
        incline_level = max(round(step['incline'] / 0.5) * 0.5, args.min_incline)
        start = round(step['cumulative_distance'] * 100) / 100
        if args.step_print:
            print(F"""{i + 1} / {len(steps)} ({up_down}): At {start}{args.unit}, set to incline {incline_level}%""")
        else:
            print (F"""Step {i + 1} ({up_down})
\tIncline : {incline_level}%
\tStep Distance: {round (step['distance'] * 100) / 100}{args.unit}
\tStart this step at: {start}{args.unit}\
""")
        final_dis = step['cumulative_distance'] + step['distance']
    print(F"Final Distance: {round(final_dis * 10) / 10}{args.unit}")

def combine_steps(steps, combine_within = 2):
    incline_amt = float("Inf")
    new_steps = []
    for step in steps:
        if abs(step['incline'] - incline_amt) < combine_within:
            # Keeping these as part of the same, inc distance
            new_steps[-1]['distance'] += step['distance']
        else:
            new_steps.append(step)
            incline_amt = step['incline']
    return new_steps

# Now go through the list of treadmill steps + combine ones that are similar
treadmill_steps = combine_steps(treadmill_steps, args.percent_combine)
print_steps(treadmill_steps)

if not args.no_graph:
    plt.plot(elevation_points)
    plt.plot(smoothed_grades)
    plt.show()