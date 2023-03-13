
import folium
from streamlit_folium import folium_static


def create_tooltip(workout_info):
    try:
        tooltip = workout_info["uuid"]
    except:
        tooltip = ""
    return tooltip


def create_marker(latitude, longitude, workout_info, map_handle):
    folium.Marker(
        icon=folium.Icon(icon="play-circle", size=10),
        location=[latitude, longitude],
        # popup=
        tooltip=create_tooltip(workout_info),
    ).add_to(map_handle)


def plot_walk_points(walk_points, map_handle, linecolour, linewidth, workout_info):
    folium.PolyLine(walk_points, color=linecolour, weight=linewidth).add_to(map_handle)
    # if start_date and time_hours and distance_km is not None:
    create_marker(walk_points[0][0], walk_points[0][1], workout_info, map_handle)


def create_walk_map_handle(query_df, map_handle, workout_info):
    plot_walk_points(query_df.values, map_handle, "blue", 3, workout_info)


def create_walk_map(query_df, workout_info):
    start_coord = (0, 0)
    map_handle = folium.Map(
        start_coord, zoom_start=13, detect_retina=True, control_scale=True
    )
    plot_walk_points(query_df.values, map_handle, "blue", 3, workout_info)
    map_handle.fit_bounds(map_handle.get_bounds())
    folium_static(map_handle, width=550, height=300)