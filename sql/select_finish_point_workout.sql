-- Get finishing point for each workout
select
  finish_datetime,
  finish_latitude,
  finish_longitude,
  finish_altitude,
  finish_speed,
  workout_id
from
  (
    select
      date as finish_datetime,
      latitude as finish_latitude,
      longitude as finish_longitude,
      altitude as finish_altitude,
      speed as finish_speed,
      workout_id,
      row_number() over (
        partition by workout_id
        order by
          date desc
      ) as date_rank
    from
      workout_points
  )
where
  date_rank = 1