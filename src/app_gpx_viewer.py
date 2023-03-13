import warnings
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
from gpx_converter import Converter


warnings.simplefilter(action="ignore", category=FutureWarning)

@dataclass
class Track:
    name: str
    date: datetime.date
    time: datetime.time
    data: pd.DataFrame


st.set_page_config(
    page_title="Emmaus-Walking-Data",
    layout="wide",
    menu_items={
        "About": "Created with love & care at DataBooth - www.databooth.com.au"
    },
)


def extract_track_metadata(gpx_file):
    if gpx_file is not None:
        tmp = gpx_file.name.replace("route_", "").replace(".gpx", "").replace("_", " ")
        track_date = datetime.strptime(tmp, "%Y-%m-%d %H.%M%p")
        track_df = Converter(input_file=gpx_file).gpx_to_dataframe()
        track = Track(name="undefined", date=track_date.date(), time=track_date.time(), data=track_df)
        return track
    else:
        return Track()


# Start of App

# gpx_file = st.file_uploader(label="Choose GPX file to view", type="gpx") -- use absolute path instead of file uploader

st.header("GPX viewer")

gpx_file = st.text_input(label="GPX path/filename")

if gpx_file is not None:
    if Path(gpx_file).exists():
        st.write(Path(gpx_file).name)
        track = extract_track_metadata(Path(gpx_file))
        st.write(track.data)
    else:
        st.error(f"File {gpx_file} does not exist")

