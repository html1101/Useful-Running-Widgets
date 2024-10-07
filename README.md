# Useful Running Widgets

## Route -> Treadmill (`read_profile.py`)

Converts any *.gpx route into an easy-to-use treadmill workout! Can use to simulate a given race (ex. a set of tricky hills). Most races come with a course map that can be converted into a route on Strava, or directly exported as a GPX file.

This functions by measuring the average slope across the map, then using that to calculate uphills, downhills (which are converted to a 0 inline, since a downhill can't be simulated on the treadmill), and flats. These are then used to make a step-by-step plan of what incline to run on for different lengths. A sample output:
```
Step 1 (Hill)
	Incline : 2.0%
	Step Distance: 0.79mi
	Start this step at (mi): 0.0mi
Step 2 (Hill)
	Incline : 9.5%
	Step Distance: 0.51mi
	Start this step at (mi): 0.79mi
Step 3 (Flat)
	Incline : 0.0%
	Step Distance: 1.34mi
	Start this step at (mi): 1.29mi
Step 4 (Hill)
	Incline : 11.5%
	Step Distance: 0.23mi
	Start this step at (mi): 2.63mi
Step 5 (Hill)
	Incline : 1.5%
	Step Distance: 2.85mi
	Start this step at (mi): 2.86mi
Step 6 (Hill)
	Incline : 6.5%
	Step Distance: 0.26mi
	Start this step at (mi): 5.71mi
Step 7 (Flat)
	Incline : 0.0%
	Step Distance: 1.28mi
	Start this step at (mi): 5.97mi
Step 8 (Hill)
	Incline : 2.0%
	Step Distance: 0.33mi
	Start this step at (mi): 7.25mi
Step 9 (Hill)
	Incline : 6.0%
	Step Distance: 0.22mi
	Start this step at (mi): 7.59mi
Total Distance: 7.81mi
```
Available options can be viewed using `python3 read_profile.py --help`:
```
options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        GPX file to analyze.
  -u {mi,km}, --unit {mi,km}
                        Whether to use kilometers or miles. Default miles.
  -ng, --no-graph       Disable graph of elevation profile or not.
  -m MIN_INCLINE, --min-incline MIN_INCLINE
                        Minimum incline permitted. Default value 0.
  -n NUM_STEPS, --num-steps NUM_STEPS
                        Maximum number of steps. If not specified, no upper
                        bound.
  -p PERCENT_COMBINE, --percent-combine PERCENT_COMBINE
                        Percentage similarity in incline two steps must be for
                        them to be combined. Default 2%.
  -s, --step-print      Whether or not to use alternative output format
                        (designed more for quickly reading on treadmill).
```
To effectively capture routes with sharper, more sudden drops and inclines, 
I would recommend manually specifying the number of steps, and messing around with 
what looks like it gets those shifts (you can check by looking at the graph).