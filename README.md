# `emmaus-walking-data`

The code in this repo is designed to convert [Apple HealthKit](https://developer.apple.com/health-fitness/) data archive (export.zip) into 
a SQLite database and then pre-calculate various quantities to assist with the labelling
(grouping) of walk/hike workouts and preparing them for consumption in the main app.


### HealthKit to SQLite

This excellent tool allows one to convert an Apple Healthkit `export.zip` to an SQLite database. It performs the initial heavy lifting to convert the XML to SQLite.


### SQL queries

Are located in the `sql` directory. There are 3 relevant queries:
1. `select_star_walking_workouts.sql`
2. `select_start_point_workout.sql`
3. `select_finish_point_workout.sql`

For my specific purposes I have focussed on workout types of "Walking" or "Hiking", although you could change this in the first query if you are interested in other activity types.
`workoutactivitytype` is `HKWorkoutActivityTypeWalking` or `HKWorkoutActivityTypeHiking`.

The determination of the start / finish latitude and longitude points for each workout is performed be the other two queries.

https://developer.apple.com/documentation/healthkit/hkworkout
### App Functionality

The app `app_prepare_data.py` has three pieces of functionality which can be selected in
the main menu section of the app sidebar. These are:
1. Convert HealthKit export to SQLite
2. Pre-calculate workout summary, and
3. Label/group walks.

#### Convert HealthKit export to SQLite

Choose _Export All Health Data_ on your iPhone and save the generated file (`export.zip`) somewhere convenient.
Specify the location (path) of the `export.zip` that you wish to convert to a SQLite database.
The button only becomes active when a valid location in provided. Press the button to perform the conversion (which typically should take 2-3 minutes to complete).


#### Pre-calculate workout summary

Performs the SQL queries detailed above to select all walking and hiking related workouts and then enriches this summary of workouts with the start and finish points and optionally (by selecting the check box) determines the named location of the start and finish location to assist with identifying the walk (note that this process takes some time.)

The most recent database is reported in data directory.

#### Label/group walks