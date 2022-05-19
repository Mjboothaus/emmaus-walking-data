from numpy import empty
import streamlit as st
import pandas as pd
from pathlib import Path
from sqlite_utils import Database
from streamlit_folium import folium_static
import folium
from st_aggrid import AgGrid

# Labelling / grouping approach relies on the sorting by workout start time

st.set_page_config(layout="wide")

def plot_walk_points(walk_points, map_handle, linecolour, linewidth):
    folium.PolyLine(walk_points, color=linecolour, weight=linewidth).add_to(map_handle)

def create_walk_map(query_df):
    start_coord = (0, 0)
    map_handle = folium.Map(start_coord, zoom_start=13, detect_retina=True, control_scale=True)
    plot_walk_points(query_df.values, map_handle, 'blue', 3)
    map_handle.fit_bounds(map_handle.get_bounds())
    folium_static(map_handle, width=500, height=200)

def save_workout_label(workout_id, walk_group):
  with open("data/workouts_labelled.csv", "a") as f:
    csv_str = "\n" + workout_id + "," + str(walk_group)
    f.write(csv_str)

def save_new_walk_group(walk_group, walk_group_name):
  with open("data/walk_groups.csv", "a") as f:
    csv_str = "\n" + '"' + str(walk_group).upper() + '","'  + walk_group_name + '"'
    f.write(csv_str)

db = Database(Path("/Users/mjboothaus/icloud/Data/apple_health_export/healthkit_db_2022_05_11.sqlite"))

# Create a button to run conversion script & calculation of workouts_summary

DATA_URL = Path("data/workouts_summary.xlsx")
data_df = pd.read_excel(DATA_URL, parse_dates=["start_datetime"])
data_df.sort_values(by="start_datetime", inplace=True)
data_df.reset_index(inplace=True)
data_df["index"] = data_df.index

walk_groups_df = pd.read_csv("data/walk_groups.csv")
walk_group = walk_groups_df["walk_group"].to_list()

workouts_labelled_df = pd.read_csv("data/workouts_labelled.csv")
last_labelled_workout_id = workouts_labelled_df.loc[workouts_labelled_df.index[-1], "workout_id"]

display_columns = [
  "index",
  "start_datetime",
  # "start_latitude",
  # "start_longitude",
  # "start_altitude",
  # "start_speed",
  #"walk_group",
  "workout_id",
  #"finish_datetime",
  #"finish_latitude",
  #"finish_longitude",
  #"finish_altitude",
  #"finish_speed",
  "start_location",
  "finish_location",
  "elapsed_time_hours",
  # "duration_minutes",
  "totaldistance_km"]
  # "totalenergyburned_kJ",
  # "sourceName",
  # "sourceVersion",
  # "startDate",
  # "endDate",
  # "metadata_HKWeatherTemperature",
  # "metadata_HKWeatherHumidity",
  # "metadata_HKElevationAscended",
  # "metadata_HKAverageMETs",
  # "index"]

# sidebar

placeholder1 = st.sidebar.empty()
placeholder2 = st.sidebar.empty()

input1 = placeholder1.text_input("New walk group e.g. GNW")
input2 = placeholder2.text_input("New walk group name e.g. Great North Walk")

save_group = st.sidebar.button("Save new walk group", key=1)

if save_group and len(input1) > 2:
    save_new_walk_group(input1, input2)
    input1 = placeholder1.text_input("New walk group e.g. GNW", value="", key=1)
    input2 = placeholder2.text_input("New walk group name e.g. Great North Walk", value="", key=1)
    # update walk_group info if new group created   
    walk_groups_df = pd.read_csv("data/walk_groups.csv")
    walk_group = walk_groups_df["walk_group"].to_list()
  
st.sidebar.markdown('##')

display_all = st.sidebar.checkbox("Display all workouts (in grid)")
st.sidebar.markdown('##')

threshold = st.sidebar.slider("Minimum distance threshold (km)", 0, 10, 1)

# filter data & do calculations

data_filtered_df = data_df[data_df["totaldistance_km"] >= threshold]
data_filtered_df.reset_index(drop=True, inplace=True)

next_row_index = data_filtered_df["workout_id"].loc[data_filtered_df["workout_id"] == last_labelled_workout_id].index + 1

next_row = data_filtered_df[display_columns].loc[next_row_index]
next_workout_id = next_row["workout_id"].iloc[0]

# main page

st.header("HealthKit workout labeller")

if display_all is True:
  st.markdown("### All workouts - " + str(len(data_filtered_df)))
  grid = AgGrid(data_filtered_df[display_columns], editable=True)
  grid_df = grid["data"]

st.write("### Next workout to label")

query = 'SELECT latitude, longitude FROM workout_points WHERE workout_id = "'
query += next_workout_id + '"'

st.write(data_filtered_df[display_columns][data_filtered_df["workout_id"] == next_workout_id].T)

query_df = pd.read_sql_query(query, db.conn)
create_walk_map(query_df)

walk_group_selected = st.selectbox("Walk group label?", walk_group)

st.write(walk_groups_df["walk_group_name"][walk_groups_df["walk_group"] == walk_group_selected].iloc[0])

if st.button("Save walk label"):
  save_workout_label(next_workout_id, walk_group_selected)
  st.info("File saved")
  st.experimental_rerun()