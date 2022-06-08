# `emmaus-walking-data`

The code in this repo is designed to convert the data in an [Apple HealthKit](https://developer.apple.com/health-fitness/) archive (export.zip) into 
a SQLite database and then pre-calculate various quantities to assist with the labelling
(grouping) of walk/hike workouts and preparing them for consumption for mapping the groups of walks/hikes.

For the specific purposes here I have focussed on workout types of "Walking" or "Hiking", although you could change this in the first query (`select_star_walking_workouts.sql`) below if you are interested in other [workout](
https://developer.apple.com/documentation/healthkit/hkworkout) types.
`workoutactivitytype` is `HKWorkoutActivityTypeWalking` or `HKWorkoutActivityTypeHiking`.

The determination of the start / finish latitude and longitude points for each workout is performed by the other two queries.

### App Functionality

The app `app_prepare_data.py` has three pieces of functionality which can be selected in
the main menu section of the app sidebar. These are:
1. Convert the HealthKit export to a SQLite database
2. Pre-calculate summary data for each walk/hike workout in the HealthKit data
3. Facilitate the labelling/group of walks, and
4. Mapping of each of the labelled walks.

#### Convert HealthKit export to SQLite

Choose _Export All Health Data_ on your iPhone and save the generated file (`export.zip`) somewhere convenient.

Specify the location (path) of the `export.zip` that you wish to convert to a SQLite database.
The button only becomes active when a valid location in provided. Press the button to perform the conversion (which typically should take 2-3 minutes to complete).

Input:
- `export.zip`

Output:
- `data/healthkit_db_*.sqlite` converted version(s) of HealthKit data as a SQLite database.

This excellent [healthkit-to-sqlite](https://github.com/dogsheep/healthkit-to-sqlite) tool allows one to convert an Apple Healthkit `export.zip` to an SQLite database. It performs the initial heavy lifting to convert the underlying XML archive to SQLite.

#### Pre-calculate Workout Summary

Performs the SQL queries detailed above to select all walking and hiking related workouts and then enriches this summary of workouts with the start and finish points and optionally (by selecting the check box) determines the named location of the start and finish location to assist with identifying the walk (note that this process takes some time.)

The most recent database is reported in data directory.

Input:
- `data/healthkit_db_*.sqlite` uses the most recent version of the SQLite database version of HealthKit data (usually generated in the previous step).

Output:
- `data/workouts_summary.csv`

The SQL queries are located in the `sql` directory. There are 3 relevant queries:
1. `select_star_walking_workouts.sql` - extract all of the walking and hiking workouts
2. `select_start_point_workout.sql` - for each workout determine the starting latitude and longitude
3. `select_finish_point_workout.sql` - for each workout determine the finishing latitude and longitude.

#### Label/group walks



How the labelling (grouping) works. First select the option from the main menu.

The labelling has a simple design - aiming at a 'one-pass' approach.

##### Sidebar

New walk groups can be added in the sidebar at any time. Initially there are no groups defined (hence the walk group label dropdown is greyed out with no options to select). These walk groups are stored in the file `data/walk_groups.csv` with two columns `walk_group` (the chosen short-name/abbreviation and `walk_group_name` (the full name of the walk).

The minimum distance threshold (in km) slider can be used for excluding walks/hikes under a chosen length and these are removed from the set of walks to be labelled. Currently the maximum minimum distance threshold that can be chosen is 10km - this can be changed in the code via `MAX_MIN_DISTANCE_THRESHOLD`. If this distance is greater than the longest actual walk distance then it resets to this shorter distance (rounded up to the nearest integer).

The checkbox "Display workout summary", when selected, displays a grid view of all of the walks within the set to be labelled for information purposes.


Labelling workflow...

Input:
`data/workouts_summary.csv`

Input / Output:
`data/walk_groups.csv`
`data/workouts_labelled.csv`

Not that if the session terminates before labelling is complete than you should be able to recommence provided the minimum distance threshold is reset to the value used previously.

#### Mapping the labelled walks

TODO: Complete


##### Timezone

The author's use case was for where most walks have been done in, and thus converted to, the Australian Eastern time zone. 
#### Running the Apps

The apps are developed using [Streamlit.io](https://streamlit.io) under Python 3.9.

Create a `venv` and install the `requirements.txt`. e.g.

```
python3 -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt 
```

Run the app from the `venv` using:
`streamlit run src/app_prepare_data.py`
