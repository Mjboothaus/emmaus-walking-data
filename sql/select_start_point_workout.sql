-- Get starting point for each workout
select
  start_datetime,
  start_latitude,
  start_longitude,
  start_altitude,
  start_speed,
  workout_id
from
  (
    select
      date as start_datetime,
      latitude as start_latitude,
      longitude as start_longitude,
      altitude as start_altitude,
      speed as start_speed,
      workout_id,
      row_number() over (
        partition by workout_id
        order by
          date asc
      ) as date_rank
    from
      workout_points
  )
where
  date_rank = 1