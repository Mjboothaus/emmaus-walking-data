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
`workoutactivitytype = "HKWorkoutActivityTypeWalking" or "HKWorkoutActivityTypeHiking"`.

The determination of the start / finish latitude and longitude points for each workout is performed be the other two queries.

https://developer.apple.com/documentation/healthkit/hkworkout
### App Functionality

The app `app_label_workouts.py` [TODO: Rename this app] has two pieces of functionality i.e.
i. Convert HealthKit export to DB and ii. Label/group walks.

#### Conversion



#### Label/group walks