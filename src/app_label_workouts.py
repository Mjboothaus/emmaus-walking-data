from numpy import empty
import streamlit as st
import pandas as pd
from pathlib import Path
from sqlite_utils import Database
from streamlit_folium import folium_static
import folium
from st_aggrid import AgGrid

st.set_page_config(layout="wide")

def plot_walk_points(walk_points, map_handle, linecolour, linewidth):
    folium.PolyLine(walk_points, color=linecolour, weight=linewidth).add_to(map_handle)

db = Database(Path("/Users/mjboothaus/icloud/Data/apple_health_export/healthkit_db_2022_04_28.sqlite"))

DATA_URL = Path("data/walk_info_df.xlsx")
data = pd.read_excel(DATA_URL, parse_dates=["start_datetime"])


df = data.copy()
df.sort_values(by="start_datetime", inplace=True)
df.reset_index(inplace=True)

df["index"] = df.index

# Select some rows using st.multiselect. This will break down when you have >1000 rows.

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


st.markdown("### Full Dataset")

grid = AgGrid(df[display_columns], editable=True)
grid_df = grid["data"]

selected_indices = st.multiselect('Select rows:', df.index)

walk_group_options = ["nan", "GNW1", "GWW1"]

if selected_indices != []:

    st.write('### Selected Rows')

    for row in selected_indices:
        selected_row = df[display_columns].loc[row]
        print(selected_row)
        st.write(selected_row)

        walk_group = st.selectbox("Walk group?", walk_group_options)
        # st.write(walk_group)

        if walk_group != "nan":
            df["walk_group"].loc[row] = walk_group

        query = 'SELECT latitude, longitude FROM workout_points WHERE workout_id = "'
        query += selected_row['workout_id'] + '"'

        data_df = pd.read_sql_query(query, db.conn)

        start_coord = (0, 0)

        map_handle = folium.Map(start_coord, zoom_start=13, detect_retina=True, control_scale=True)
        plot_walk_points(data_df.values, map_handle, 'blue', 3)
        map_handle.fit_bounds(map_handle.get_bounds())
        folium_static(map_handle, width=500, height=200)