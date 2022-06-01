from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from sqlite_utils import Database
from st_aggrid import AgGrid
from streamlit_folium import folium_static

st.set_page_config(layout="wide")


def plot_walk_points(walk_points, map_handle, linecolour, linewidth):
    folium.PolyLine(walk_points, color=linecolour, weight=linewidth).add_to(map_handle)


def create_walk_map(query_df, map_handle):
    plot_walk_points(query_df.values, map_handle, "blue", 3)


def get_latest_sqlite_file(data_dir, file_pattern="healthkit_db_*.sqlite"):
    return max(Path(data_dir).glob(file_pattern), key=lambda f: f.stat().st_ctime)


db = Database(get_latest_sqlite_file(Path(__file__).parent.parent / "data"))

# Load data & labels

DATA_URL = Path("data/workouts_summary.csv")
data_df = pd.read_csv(DATA_URL, parse_dates=["start_datetime"])
walk_groups_df = pd.read_csv("data/walk_groups.csv")
walk_group = walk_groups_df["walk_group"].to_list()
workouts_labelled_df = pd.read_csv("data/workouts_labelled.csv")

# sidebar

walk_group_selected = st.sidebar.selectbox("Walk group label?", walk_group)


# Data calculations

data_labelled_df = data_df.merge(workouts_labelled_df, on="workout_id")

# main page

st.header("Map walks")

st.write(
    walk_groups_df["walk_group_name"][
        walk_groups_df["walk_group"] == walk_group_selected
    ].iloc[0]
)

start_coord = (0, 0)
map_handle = folium.Map(
    start_coord, zoom_start=13, detect_retina=True, control_scale=True
)

workouts_to_map = data_labelled_df[
    data_labelled_df["walk_group"] == walk_group_selected
]["workout_id"].to_list()

for workout_id in workouts_to_map:
    query = 'SELECT latitude, longitude FROM workout_points WHERE workout_id = "'
    query += workout_id + '"'
    query_df = pd.read_sql_query(query, db.conn)
    create_walk_map(query_df, map_handle)

map_handle.fit_bounds(map_handle.get_bounds())
folium_static(map_handle, width=500, height=500)