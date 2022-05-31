import os
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from numpy import empty
from sqlite_utils import Database
from st_aggrid import AgGrid
from streamlit_folium import folium_static

from healthkit_to_sqlite import (
    convert_healthkit_export_to_sqlite,
    create_walk_workout_summary,
)

# Labelling / grouping approach relies on the sorting by workout start time

st.set_page_config(layout="wide")


def plot_walk_points(walk_points, map_handle, linecolour, linewidth):
    folium.PolyLine(walk_points, color=linecolour, weight=linewidth).add_to(map_handle)


def create_walk_map(query_df):
    start_coord = (0, 0)
    map_handle = folium.Map(
        start_coord, zoom_start=13, detect_retina=True, control_scale=True
    )
    plot_walk_points(query_df.values, map_handle, "blue", 3)
    map_handle.fit_bounds(map_handle.get_bounds())
    folium_static(map_handle, width=500, height=200)


def save_workout_label(workout_id, walk_group):
    with open("data/workouts_labelled.csv", "a") as f:
        csv_str = "\n" + workout_id + "," + str(walk_group)
        f.write(csv_str)


def save_new_walk_group(walk_group, walk_group_name):
    with open("data/walk_groups.csv", "a") as f:
        csv_str = "\n" + '"' + str(walk_group).upper() + '","' + walk_group_name + '"'
        f.write(csv_str)


def get_latest_sqlite_file(data_dir, file_pattern="healthkit_db_*.sqlite"):
    return max(Path(data_dir).glob(file_pattern), key=lambda f: f.stat().st_ctime)


# Start with export.zip

menu_choice = st.sidebar.radio(
    "Main menu:",
    [
        "Convert HealthKit export to SQLite",
        "Calculate workout summary",
        "Label/group walks",
    ],
)

if menu_choice == "Convert HealthKit export to SQLite":
    st.subheader("Convert HealthKit data (export.zip) to SQLite database")

    data_dir = Path(__file__).parent.parent / "data"
    st.text_input(
        label="Most recent SQLite database (in data directory)",
        value=get_latest_sqlite_file(data_dir),
    )

    path_export_zip = st.text_input(label="Enter path to export.zip")
    disabled = path_export_zip == "" or Path(path_export_zip).exists() is False

    if convert_button := st.button("Convert export.zip", disabled=disabled):
        with st.spinner(text="In progress..."):
            db_file, _ = convert_healthkit_export_to_sqlite(Path(path_export_zip))
        st.write(db_file)

elif menu_choice == "Calculate workout summary":
    st.subheader("Calculate workout summary")
    data_dir = Path(__file__).parent.parent / "data"
    db_file = get_latest_sqlite_file(data_dir)
    st.text_input(
        label="Most recent SQLite database (in data directory)", value=db_file
    )

    include_location = st.checkbox(
        "Include location lookup for start/finish points? [this takes much longer to run]"
    )

    if calc_button := st.button(label="Calculate summary"):
        with st.spinner(text="In progress..."):
            summary_file = create_walk_workout_summary(
                db_file, include_location=include_location
            )
        st.write(summary_file)
else:

    db = Database(get_latest_sqlite_file(Path(__file__).parent.parent / "data"))

    DATA_URL = Path("data/workouts_summary.xlsx")
    data_df = pd.read_excel(DATA_URL, parse_dates=["start_datetime"])
    data_df.sort_values(by="start_datetime", inplace=True)
    data_df.reset_index(inplace=True)
    data_df["index"] = data_df.index

    if Path("data/walk_groups.csv").exists() is True:
        walk_groups_df = pd.read_csv("data/walk_groups.csv")
        walk_group = walk_groups_df["walk_group"].to_list()
    else:
        # Create default walk_groups.csv
        walk_group = []
        with open("data/walk_groups.csv", "a") as walk_groups_csv:
            walk_groups_csv.write('"walk_group","walk_group_name"')

    if Path("data/workouts_labelled.csv").exists() is True:
        data_unlabelled = False
        workouts_labelled_df = pd.read_csv("data/workouts_labelled.csv")
        if workouts_labelled_df.empty:
            last_labelled_workout_id = 0
            data_unlabelled = True
        else:
            last_labelled_workout_id = workouts_labelled_df.loc[
                workouts_labelled_df.index[-1], "workout_id"
        ]
    else:
        data_unlabelled = True
        last_labelled_workout_id = 0
        with open("data/workouts_labelled.csv", "a") as workouts_labelled_csv:
            workouts_labelled_csv.write("workout_id,walk_group")

    if "start_location" in data_df.keys() and "finish_location" in data_df.keys():
        display_columns = [
            "index",
            "start_datetime",
            "workout_id",
            "start_location",
            "finish_location",
            "elapsed_time_hours",
            "totaldistance_km",
        ]
    else:
        display_columns = [
            "index",
            "start_datetime",
            "workout_id",
            "elapsed_time_hours",
            "totaldistance_km",
        ]

    # Sidebar

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
        walk_groups_df = pd.read_csv("data/walk_groups.csv")
        walk_group = walk_groups_df["walk_group"].to_list()

    st.sidebar.markdown("##")

    display_all = st.sidebar.checkbox("Display all workouts (in grid)")
    st.sidebar.markdown("##")

    threshold = st.sidebar.slider("Minimum distance threshold (km)", 0, 10, 1)

    # filter data & do calculations

    data_filtered_df = data_df[data_df["totaldistance_km"] >= threshold]
    data_filtered_df.reset_index(drop=True, inplace=True)

    if data_unlabelled:
        next_row_index = 0
    else:
        next_row_index = (
            data_filtered_df["workout_id"]
            .loc[data_filtered_df["workout_id"] == last_labelled_workout_id]
            .index
            + 1
        )

    if next_row_index >= len(data_filtered_df):
        st.write(next_row_index, len(data_filtered_df))
        st.info("Finished labelling - stopping")
    else:
        next_row = data_filtered_df[display_columns].loc[next_row_index]
        next_workout_id = next_row["workout_id"].iloc[0]

        # Main page

        st.header("Workout/group labeller")

        if display_all is True:
            st.markdown(f"### All workouts - {len(data_filtered_df)}")
            grid = AgGrid(data_filtered_df[display_columns], editable=True)
            grid_df = grid["data"]

        st.write("### Next workout to label")

        query = 'SELECT latitude, longitude FROM workout_points WHERE workout_id = "'
        query += next_workout_id + '"'

        st.write(
            data_filtered_df[display_columns][
                data_filtered_df["workout_id"] == next_workout_id
            ].T
        )

        query_df = pd.read_sql_query(query, db.conn)
        create_walk_map(query_df)

        walk_group_selected = st.selectbox("Walk group label?", walk_group)

        if walk_group != []:
            st.write(
                walk_groups_df["walk_group_name"][
                    walk_groups_df["walk_group"] == walk_group_selected
                ].iloc[0]
            )

        if st.button("Save walk label"):
            save_workout_label(next_workout_id, walk_group_selected)
            st.info("File saved")
            st.experimental_rerun()
