import warnings
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from sqlite_utils import Database
from st_aggrid import AgGrid
from streamlit_folium import folium_static

from walk_data_aux import (
    convert_healthkit_export_to_sqlite,
    create_walk_workout_summary,
)

warnings.simplefilter(action="ignore", category=FutureWarning)

# Labelling / grouping approach assumes the sorting by workout start time

MAX_MIN_DISTANCE_THRESHOLD = 50
DATA_WALK_GROUPS_CSV = "data/walk_groups.csv"

st.set_page_config(
    page_title="Emmaus-Walking-Data",
    layout="wide",
    menu_items={
        "About": "Created with love & care at DataBooth - www.databooth.com.au"
    },
)


def create_tooltip(start_date, time_hours, distance_km):
    tooltip = start_date
    return tooltip


def create_marker(latitude, longitude, start_date, time_hours, distance_km, m):
    folium.Marker(
        icon=folium.Icon(icon="play-circle"),
        location=[latitude, longitude],
        # popup=
        tooltip=create_tooltip(start_date, time_hours, distance_km),
    ).add_to(m)


def plot_walk_points(
    walk_points, map_handle, linecolour, linewidth
):  # , start_date, time_hours, distance_km):
    folium.PolyLine(walk_points, color=linecolour, weight=linewidth).add_to(map_handle)
    # if start_date and time_hours and distance_km is not None:
    #    create_marker(walk_points[0][0], walk_points[0][1], start_date, time_hours, distance_km, map_handle)


def create_walk_map_handle(
    query_df, map_handle
):  # , start_date, time_hours, distance_km):
    plot_walk_points(
        query_df.values, map_handle, "blue", 3
    )  # , start_date, time_hours, distance_km)


def create_walk_map(query_df):
    start_coord = (0, 0)
    map_handle = folium.Map(
        start_coord, zoom_start=13, detect_retina=True, control_scale=True
    )
    plot_walk_points(query_df.values, map_handle, "blue", 3) # , None, None, None)
    map_handle.fit_bounds(map_handle.get_bounds())
    folium_static(map_handle, width=550, height=300)


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
        st.error(e)
        return None, None, None


def query_workout_points(workout_id):
    return f'SELECT latitude, longitude FROM workout_points WHERE workout_id = "{workout_id}"'


def convert_healthkit_to_sqlite():
    st.subheader("Convert HealthKit data (export.zip) to SQLite database")

    placeholder = st.empty()

    data_dir = Path(__file__).parent.parent / "data"
    db_path = placeholder.text_input(
        label="Most recent SQLite database (in data directory)",
        value=get_latest_sqlite_file(data_dir)[0],
    )

    path_export_zip = st.text_input(label="Enter path to export.zip")
    disabled = path_export_zip == "" or Path(path_export_zip).exists() is False

    if convert_button := st.button("Convert export.zip", disabled=disabled, key=1):
        with st.spinner(text="In progress..."):
            db_file_data_dir, mv_zip_file = convert_healthkit_export_to_sqlite(Path(path_export_zip))
        if Path(db_file_data_dir).exists():
            db_path = placeholder.text_input(
                label="Most recent SQLite database (in data directory)",
                value=db_file_data_dir,
                key=1,
            )
            st.markdown("##")
            st.info("Export successful: export.zip renamed to " + mv_zip_file)


def calculate_workout_summary():
    st.subheader("Calculate workout summary")
    data_dir = Path(__file__).parent.parent / "data"
    db_file, db_available = get_latest_sqlite_file(data_dir)
    st.text_input(
        label="Most recent SQLite database (in data directory)", value=db_file
    )
    disable_calc_button = db_available == 0
    if st.button(label="Calculate summary", disabled=disable_calc_button):
        with st.spinner(text="In progress..."):
            summary_file = create_walk_workout_summary(db_file)
        st.write(summary_file)


def label_group_walks():
    db_path, db_available = get_latest_sqlite_file(
        Path(__file__).parent.parent / "data"
    )
    if db_available == 0:
        st.info(
            "No SQLite database available: please first convert HealthKit export (menu option 1)"
        )
        return None

    # Load data

    db = Database(db_path)

    try:
        DATA_CSV = Path("data/workouts_summary.csv")
        data_df = pd.read_csv(DATA_CSV, parse_dates=["start_datetime"])
        data_df.sort_values(by="start_datetime", inplace=True)
        data_df.reset_index(inplace=True)
        data_df["index"] = data_df.index
    except IOError as e:
        st.error(e)
        return

    if Path(DATA_WALK_GROUPS_CSV).exists():
        walk_groups_df = pd.read_csv(DATA_WALK_GROUPS_CSV)
        walk_group = walk_groups_df["walk_group"].to_list()
    else:
        # Create default walk_groups.csv
        walk_group = []
        with open(DATA_WALK_GROUPS_CSV, "a") as walk_groups_csv:
            walk_groups_csv.write('"walk_group","walk_group_name"')

    if Path("data/workouts_labelled.csv").exists():
        data_labelled = True
        workouts_labelled_df = pd.read_csv("data/workouts_labelled.csv")
        if workouts_labelled_df.empty:
            last_labelled_workout_id = 0
            data_labelled = False
        else:
            last_labelled_workout_id = workouts_labelled_df.loc[
                workouts_labelled_df.index[-1], "workout_id"
            ]
    else:
        data_labelled = False
        last_labelled_workout_id = 0
        with open("data/workouts_labelled.csv", "a") as workouts_labelled_csv:
            workouts_labelled_csv.write("workout_id,walk_group")

    # Sidebar
    st.sidebar.text_input(label="SQLite database", value=db_path.split("/")[-1])
    st.sidebar.markdown("## Add new walk group")

    placeholder1 = st.sidebar.empty()
    placeholder2 = st.sidebar.empty()

    input1 = placeholder1.text_input("New walk group e.g. GNW")
    input2 = placeholder2.text_input("New walk group name e.g. Great North Walk")

    save_group = st.sidebar.button("Save new walk group", key=1)

    if save_group and len(input1) > 2:
        save_new_walk_group(input1, input2)
        input1 = placeholder1.text_input("New walk group e.g. GNW", value="", key=1)
        input2 = placeholder2.text_input(
            "New walk group name e.g. Great North Walk", value="", key=1
        )
        # update walk_group info if new group created
        walk_groups_df = pd.read_csv(DATA_WALK_GROUPS_CSV)
        walk_group = walk_groups_df["walk_group"].to_list()

    st.sidebar.markdown("##")

    MAX_WALK_LENGTH = data_df["totaldistance_km"].max()
    threshold = st.sidebar.slider(
        "Minimum distance threshold (km)",
        0,
        int(min(MAX_MIN_DISTANCE_THRESHOLD, MAX_WALK_LENGTH)) + 1,
        0,
    )

    st.sidebar.markdown("##")

    display_all = st.sidebar.checkbox("Info: Display summary of workouts")

    # filter data & do calculations

    data_filtered_df = data_df[data_df["totaldistance_km"] >= threshold]
    data_filtered_df.reset_index(drop=True, inplace=True)

    display_columns = [
        "index",
        "start_datetime",
        "workout_id",
        "start_location",
        "finish_location",
        "elapsed_time_hours",
        "totaldistance_km",
    ]

    # if data_filtered_df["workout_id"].isin([last_labelled_workout_id]).any():
    # try:
    next_row_index = (
        data_filtered_df["workout_id"]
        .loc[data_filtered_df["workout_id"] == last_labelled_workout_id]
        .index
        + 1
        if data_labelled
        and data_filtered_df["workout_id"].isin([last_labelled_workout_id]).any()
        else 0
    )

    if next_row_index >= len(data_filtered_df):
        st.info("Finished labelling - stopping")
    else:
        # Following is a pragmatic hack as for some reason Pandas sometimes returns a dataframe with a single row, and other times as a series.
        try:
            next_row = data_filtered_df[display_columns].iloc[[next_row_index], :]
        except Exception:
            next_row = data_filtered_df[display_columns].iloc[next_row_index]

    next_workout_id = next_row["workout_id"].iloc[0]

    # Main page - Label/group walks

    if display_all:
        st.markdown(
            f"#### Walks selected (total distance > {threshold} km) : Count is {len(data_filtered_df)}"
        )
        grid = AgGrid(data_filtered_df[display_columns], editable=True)
        grid_df = grid["data"]

    st.subheader("Label/group walks")

    st.write("#### Next workout to label")

    st.write(
        data_filtered_df[display_columns][
            data_filtered_df["workout_id"] == next_workout_id
        ].T
    )

    query_df = pd.read_sql_query(query_workout_points(next_workout_id), db.conn)
    create_walk_map(query_df)

    walk_group_selected = st.selectbox("Walk group label?", walk_group)

    if walk_group != []:
        save_walk_disabled = False
        st.write(
            walk_groups_df["walk_group_name"][
                walk_groups_df["walk_group"] == walk_group_selected
            ].iloc[0]
        )
    else:
        save_walk_disabled = True

    if st.button("Save walk label", disabled=save_walk_disabled):
        save_workout_label(next_workout_id, walk_group_selected)
        st.info("File saved")
        st.experimental_rerun()


# elif not data_labelled:
#   st.error(
#        "Need to start with first workout_id"
#    )
# except:
#    st.error(
#        "Cannot find last labelled workout in walks - this may have been excluded by an increase in the distance threshold."
#    )
# return


def map_walks():
    # Load data
    data_df, walk_groups_df, workouts_labelled_df = load_data()
    if data_df is None or walk_groups_df is None or workouts_labelled_df is None:
        return None
    if workouts_labelled_df.empty:
        st.info("No workouts to map - you need to label some first.")
        return None
    db = Database(get_latest_sqlite_file(Path(__file__).parent.parent / "data")[0])

    walk_group = walk_groups_df["walk_group"].to_list()

    # sidebar
    walk_group_selected = st.sidebar.selectbox("Walk to map?", walk_group)

    st.dataframe(workouts_labelled_df)
    st.dataframe(data_df)

    # Data transformation
    data_labelled_df = data_df.merge(workouts_labelled_df, on="workout_id")

    st.write(len(data_labelled_df), len(data_df), len(workouts_labelled_df))

    # main page
    st.header("Map walks")

    st.write(
        walk_groups_df["walk_group_name"][
            walk_groups_df["walk_group"] == walk_group_selected
        ].iloc[0]
    )

    workouts_to_map = data_labelled_df[
        data_labelled_df["walk_group"] == walk_group_selected
    ]["workout_id"].to_list()

    start_coord = (0, 0)
    map_handle = folium.Map(
        start_coord, zoom_start=13, detect_retina=True, control_scale=True
    )

    for workout_id in workouts_to_map:
        query_df = pd.read_sql_query(query_workout_points(workout_id), db.conn)
        # start_date = data_df[data_df["workout_id"] == workout_id]["startDate"].iloc[0]
        # time_hours = data_df[data_df["workout_id"] == workout_id]["elapsed_time_hours"].iloc[0]
        # distance_km = data_df[data_df["workout_id"] == workout_id]["totaldistance_km"].iloc[0]
        create_walk_map_handle(
            query_df, map_handle
        )  # , start_date, time_hours, distance_km)

    map_handle.fit_bounds(map_handle.get_bounds())
    folium_static(map_handle, width=750, height=550)


# Main menu

menu_choice = st.sidebar.radio(
    "Main menu:",
    [
        "Convert HealthKit export to SQLite",
        "Calculate workouts summary",
        "Label/group walks",
        "Map walks",
    ],
)
st.sidebar.markdown("##")

if menu_choice == "Convert HealthKit export to SQLite":
    convert_healthkit_to_sqlite()
elif menu_choice == "Calculate workouts summary":
    calculate_workout_summary()
elif menu_choice == "Label/group walks":
    label_group_walks()
else:
    map_walks()
