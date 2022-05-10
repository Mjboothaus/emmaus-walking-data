select
    id as workout_id,
    duration as duration_minutes,
    totaldistance as totaldistance_km,
    totalenergyburned as totalenergyburned_kJ,
    sourcename,
    sourceversion,
    startdate,
    enddate,
    metadata_hkweathertemperature,
    metadata_hkweatherhumidity,
    metadata_hkelevationascended,
    metadata_hkaveragemets
from
    workouts
where workoutactivitytype = "HKWorkoutActivityTypeWalking" order by id


 /* Excluded fields:
    workoutactivitytype,   # just walking
    durationunit,          # fixed - min
    totaldistanceunit,     # fixed - km
    totalenergyburnedunit, # fixed - kJ
    device,
    creationdate,          # not really of interest (start date instead)
    workout_events,        # think this is redundant info (need to check - JSON?)
    metadata_hkgroupfitness,
    metadata_hkworkoutbrandname,
    metadata_hktimezone,
    metadata_hkcoachedworkout,
    metadata_hkwasuserentered,
    metadata_hkindoorworkout,
    metadata_hkelevationascended,
    metadata_hkswimminglocationtype,
    metadata_hkaveragemets,
    metadata_healthfit_sub_sport,
    metadata_healthfit_route,
    metadata_healthfit_file_type,
    metadata_hkmaximumspeed,
    metadata_healthfit_total_moving_time,
    metadata_healthfit_total_distance,
    metadata_healthfit_max_running_cadence,
    metadata_healthfit_min_altitude,
    metadata_healthfit_avg_running_cadence,
    metadata_healthfit_app_build,
    metadata_healthfit_fit_sport,
    metadata_healthfit_fit_sub_sport,
    metadata_healthfit_max_altitude,
    metadata_healthfit_fit_manufacturer,
    metadata_healthfit_total_strides,
    metadata_healthfit_fit_serial_number,
    metadata_healthfit_sport,
    metadata_hkaveragespeed,
    metadata_healthfit_app_version,
    metadata_hkexternaluuid
 */
