#  HealthKit to SQLite
#   - Export all of my Apple HealthFit data from the Health app to export.zip
#   - Converted this to a SQLite database using `healthkit-to-sqlite`
#   - Run various SQL queries to allow for producing a summary of (walk/hike) workouts

# The archive can be converted to a SQLite database using the following command:
# `healthkit-to-sqlite export.zip healthkit_db.sqlite`

import pandas as pd
import datetime as dt
from pathlib import Path
import subprocess
import pendulum
from sqlite_utils import Database
import reverse_geocoder as rg


def get_location(latitude, longitude):
    location = rg.search((latitude, longitude))
    return [location[0]["name"], location[0]["admin1"], location[0]["cc"]]


def calculate_elapsed_time_minutes(finish_datetime, start_datetime):
    dt = pendulum.parse(finish_datetime) - pendulum.parse(start_datetime)
    return float(dt.in_seconds() / 60 / 60)


def convert_healthkit_export_to_sqlite(export_zip):
    zip_file = export_zip.as_posix()
    if export_zip.exists() is False:
        print(zip_file, ": not found")
        return None, f"{zip_file}: not found"
    zip_file_date = pendulum.instance(
        dt.datetime.fromtimestamp(export_zip.stat().st_ctime)
    )

    db_file = zip_file.replace("export.zip", "healthkit_db.sqlite")
    if Path(db_file).exists() is True:
        Path(db_file).unlink()
    sp_cmd = f"healthkit-to-sqlite {zip_file} {db_file}"

    sp = subprocess.Popen(sp_cmd, stdout=subprocess.PIPE, shell=True)
    (sp_output, _) = sp.communicate()

    db_file_with_date = db_file.replace(
        ".sqlite", "_" + zip_file_date.to_date_string().replace("-", "_") + ".sqlite"
    )

    export_zip.rename(
        zip_file.replace(
            ".zip", "_" + zip_file_date.to_date_string().replace("-", "_") + ".zip"
        )
    )
    Path(db_file).rename(db_file_with_date)

    return db_file_with_date, sp_output


def create_df_from_sql_query_in_file(
    filename_dot_sql, conn, parse_dates, echo_query=False
):

    query_file = Path(__file__).parent.parent / "sql" / filename_dot_sql

    with open(query_file, "r") as query:
        sql_text = query.read()
        if echo_query is True:
            print(sql_text)
        df = pd.read_sql_query(sql_text, conn, parse_dates=parse_dates)
    return df


def create_walk_workout_summary(
    db_file, output_file=Path(__file__).parent.parent / "data/workouts_summary.xlsx", include_location=False
):
    if db_file is None or Path(db_file).exists() is False:
        print("SQLite database doesn't exist or not found")
        return None
    db = Database(db_file)

    # Extract data

    workouts_df = create_df_from_sql_query_in_file(
        "select_star_walking_workouts.sql", db.conn, ["startDate", "endDate"]
    )
    start_point_df = create_df_from_sql_query_in_file(
        "select_start_point_workout.sql", db.conn, ["date"]
    )
    finish_point_df = create_df_from_sql_query_in_file(
        "select_finish_point_workout.sql", db.conn, ["date"]
    )

    # Perform joins and additional column manipulations

    workouts_df["startDate"] = workouts_df["startDate"].apply(
        lambda dt: pendulum.instance(dt).to_datetime_string()
    )
    workouts_df["endDate"] = workouts_df["endDate"].apply(
        lambda dt: pendulum.instance(dt).to_datetime_string()
    )
    workouts_summary_df = start_point_df.merge(
        finish_point_df, how="inner", on="workout_id"
    )
    workouts_summary_df["elapsed_time_hours"] = workouts_summary_df.apply(
        lambda row: calculate_elapsed_time_minutes(
            row["finish_datetime"], row["start_datetime"]
        ),
        axis=1,
    )
    workouts_summary_df["start_datetime"] = workouts_summary_df["start_datetime"].apply(
        lambda dt: pendulum.parse(dt, tz="Australia/Sydney").to_datetime_string()
    )

    if include_location is True:
        workouts_summary_df["start_location"] = workouts_summary_df.apply(
            lambda row: get_location(
                float(row["start_latitude"]), float(row["start_longitude"])
            ),
            axis=1,
        )
        workouts_summary_df["finish_location"] = workouts_summary_df.apply(
            lambda row: get_location(
                float(row["finish_latitude"]), float(row["finish_longitude"])
            ),
            axis=1,
        )
    workouts_summary_df = workouts_summary_df.merge(
        workouts_df, how="inner", on="workout_id"
    )

    workouts_summary_df.to_excel(output_file, index=False)
    return Path(output_file)


def main_convert_create_walk_summary(path_export_zip, include_location=False):
    db_file, _ = convert_healthkit_export_to_sqlite(path_export_zip)
    output_file = create_walk_workout_summary(
        db_file, include_location=include_location
    )
    return db_file, output_file