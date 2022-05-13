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


db = Database(Path("/Users/mjboothaus/icloud/Data/apple_health_export/healthkit_db_2022_04_28.sqlite"))

DATA_URL = Path("data/walk_info_df.xlsx")
data_df = pd.read_excel(DATA_URL, parse_dates=["start_datetime"])

data_df.sort_values(by="start_datetime", inplace=True)
data_df.reset_index(inplace=True)

data_df["index"] = data_df.index

walk_groups_df = pd.read_excel("data/walk_groups.xlsx")

walk_group = walk_groups_df["walk_group"].to_list()

workout_groups_df = pd.read_csv("data/workout_groups.csv")

st.dataframe(workout_groups_df)

last_labelled_workout_id = workout_groups_df.loc[workout_groups_df.index[-1], "workout_id"]

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


# st.markdown("### Full Dataset")

grid = AgGrid(data_df[display_columns], editable=True)
grid_df = grid["data"]


next_row_index = data_df.loc[data_df["workout_id"] == last_labelled_workout_id].index + 1

# next_workout_id = data_df.loc[next_row_index]["workout_id"]

##TODO: Continue here - weird stuff happening e.g. query is a DataFrame??

st.write("### Last workout without a group")

selected_row = data_df[display_columns].loc[next_row_index]
st.write(selected_row)

walk_group_selected = st.selectbox("Walk group?", walk_group)


query = 'SELECT latitude, longitude FROM workout_points WHERE workout_id = "'
query += selected_row['workout_id'] + '"'

st.write(query)

query_df = pd.read_sql_query(query, db.conn)

create_walk_map(query_df)

st.metric(selected_row['workout_id'], walk_group_selected)

