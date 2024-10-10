# connet db file
import argparse
import pathlib
import sqlite3

import pandas as pd
from matplotlib.font_manager import FontProperties

from Database.scr.log_utils import Logging
from Visualizations.codes import (
    bar,
    map_L1_different_events,
    map_L1_overview,
    map_L2,
    map_L3,
    pie,
)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
font_prop = FontProperties(fname=font_path)

if __name__ == "__main__":
    logger = Logging.get_logger("visualization")
    available_event_levels = ["l1", "l2", "l3"]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--output_dir",
        dest="outputdir",
        help="output path for the visualization",
        type=str,
    )
    parser.add_argument(
        "-db",
        "--db_path",
        dest="db_path",
        help="db file for the visualization",
        type=str,
    )
    parser.add_argument(
        "-cn",
        "--country_path",
        dest="country_path",
        help="country_path for the visualization",
        type=str,
    )
    parser.add_argument(
        "-st",
        "--state_path",
        dest="state_path",
        help="state_path for the visualization",
        type=str,
    )
    parser.add_argument(
        "-ed",
        "--EM_DAT_path",
        dest="EM_DAT_path",
        help="EM_DAT_path for the comparison",
        type=str,
    )

    args = parser.parse_args()
    logger.info(f"Passed args: {args}")

    logger.info(f"Creating {args.output_dir} if it does not exist!")
    pathlib.Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Connect to the SQLite database
    conn = sqlite3.connect(args.db_path)
    # Query to get the names of all tables
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql_query(tables_query, conn)

    # Get the list of table names
    table_names = tables_df["name"].tolist()

    # Dictionary to store the DataFrame for each table
    tables_data = {}

    # Loop through each table name and create a DataFrame for each
    for table in table_names:
        query = f"SELECT * FROM {table}"
        tables_data[table] = pd.read_sql_query(query, conn)
        print(
            f"Table '{table}' read into DataFrame with {tables_data[table].shape[0]} rows and {tables_data[table].shape[1]} columns."
        )
    # Close the database connection
    conn.close()
    geo = tables_data["GeoJson_Obj"]
    nid_to_geo_obj = {str(nid).strip().lower(): geo_obj for nid, geo_obj in zip(geo["nid"], geo["geojson_obj"])}
    L1 = tables_data["Total_Summary"]
    instance_dfs = [
        df for key, df in tables_data.items() if key.startswith("Instance") and isinstance(df, pd.DataFrame)
    ]
    if instance_dfs:
        L2 = pd.concat(instance_dfs, ignore_index=True)
    Specific_instance_dfs = [
        df for key, df in tables_data.items() if key.startswith("Specific") and isinstance(df, pd.DataFrame)
    ]
    if Specific_instance_dfs:
        L3 = pd.concat(Specific_instance_dfs, ignore_index=True)
    # Define custom colors for each event
    custom_colors = {
        "Flood": "#000C66",  #  A navy blue.
        "Drought": "#FFD29D",  #  A light peach or pastel orange.
        "Wildfire": "#ff8882",  # A light pink.
        "Tornado": "#918450",  # A muted khaki or olive color.
        "Extratropical Storm/Cyclone": "#00AFB9",  # A vivid turquoise or teal.
        "Tropical Storm/Cyclone": "#00619c",  # A medium blue-gray or steel blue.-green
        "Extreme Temperature": "#A41623",  # A deep, dark red or crimson.
    }
    selected_event_types = [
        "Flood",
        "Drought",
        "Wildfire",
        "Tornado",
        "Extratropical Storm/Cyclone",
        "Tropical Storm/Cyclone",
        "Extreme Temperature",
    ]

    # plot pie chart for L1
    pie.plot_event_distribution_pie(
        L1,
        custom_colors,
        "Distribution of main event in Wikimpacts 1.0 database",
        f"{args.outputdir}/pie_distribution_L1_overview.pdf",
    )
    # plot bar chart for L1
    bar.plot_decadal_event_distribution(
        L1,
        custom_colors,
        "Temporal distribution of main events in Wikimpacts 1.0 database",
        f"{args.outputdir}/bar_distribution_L1_overview.pdf",
    )
    # plot L1 map for overview
    event_count_per_admin_area = map_L1_overview.count_events_per_admin_area(L1)
    map_L1_overview.plot_main_events_per_admin_area(
        L1,
        nid_to_geo_obj,
        args.country_path,
        event_count_per_admin_area,
        f"{args.outputdir}/Spatial_distribution_L1_overview.pdf",
    )
    # plot L1 map in different events
    for event in selected_event_types:
        event_count_per_admin_area = map_L1_different_events.count_events_per_admin_area(df, event)
        if event_count_per_admin_area is not None and not event_count_per_admin_area.empty:
            outputpath = f"{event.replace('/', '_')}_L1.pdf"

            map_L1_different_events.plot_main_events_per_admin_area(
                L1, nid_to_geo_obj, args.country_path, event_count_per_admin_area, outputpath, event
            )
    # plot number of impact points in L2
    event_count_per_admin_area = map_L2.count_events_per_admin_area(L2)
    map_L2.plot_main_events_per_admin_area(
        L2,
        nid_to_geo_obj,
        args.country_path,
        event_count_per_admin_area,
        f"{args.outputdir}/Spatial_distribution_L2_overview.pdf",
    )
    # plot number of impact points in L3
    event_count_per_admin_area = map_L3.count_events_per_admin_area(L3)
    map_L3.plot_main_events_per_admin_area(
        L2,
        nid_to_geo_obj,
        args.state_path,
        event_count_per_admin_area,
        f"{args.outputdir}/Spatial_distribution_L3_overview.pdf",
    )

    # plot the difference between EM-DAT (1900-20240229) with Wikimpacts L2 same time period
