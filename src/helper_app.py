from pathlib import Path
import pandas as pd


DATA_WALK_GROUPS_CSV = "data/walk_groups.csv"


def save_workout_label(workout_id, walk_group):
    with open("data/workouts_labelled.csv", "a") as f:
        csv_str = "\n" + workout_id + "," + str(walk_group)
        f.write(csv_str)


def save_new_walk_group(walk_group, walk_group_name):
    with open(DATA_WALK_GROUPS_CSV, "a") as f:
        csv_str = "\n" + '"' + str(walk_group).upper() + '","' + walk_group_name + '"'
        f.write(csv_str)


def get_latest_sqlite_file(data_dir, file_pattern="healthkit_db_*.sqlite"):
    return (
        (
            max(
                Path(data_dir).glob(file_pattern),
                key=lambda f: f.stat().st_ctime,
            )
            .absolute()
            .as_posix(),
            len(list(Path(data_dir).glob(file_pattern))),
        )
        if list(Path(data_dir).glob(file_pattern))
        else (f"No files matching {file_pattern}", 0)
    )


def load_data():
    DATA_CSV = Path("data/workouts_summary.csv")
    try:
        data_df = pd.read_csv(DATA_CSV, parse_dates=["start_datetime"])
        walk_groups_df = pd.read_csv(DATA_WALK_GROUPS_CSV)
        workouts_labelled_df = pd.read_csv("data/workouts_labelled.csv")
        return data_df, walk_groups_df, workouts_labelled_df
    except IOError as e:
        raise ("Cannot find: " + DATA_CSV.as_posix() + " - first use Menu item #2 to calculate.") from e


def query_workout_points(uuid, data_filtered_df):
    workout_id = data_filtered_df[data_filtered_df["uuid"] == uuid]["workout_id"].iloc[0]
    return f'SELECT latitude, longitude FROM workout_points WHERE workout_id = "{workout_id}"'