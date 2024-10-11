import ast

import matplotlib as plt
import numpy as np
import pandas as pd
from shapely.geometry import shape


def flatten_and_parse(lst):
    """
    Recursively flattens a nested list and safely evaluates strings representing lists.
    """
    result = []
    for item in lst:
        if isinstance(item, list) or isinstance(item, np.ndarray):
            result.extend(flatten_and_parse(item))
        elif isinstance(item, str):
            # Try to parse the string as a list
            try:
                item_parsed = ast.literal_eval(item)
                if isinstance(item_parsed, list):
                    result.extend(flatten_and_parse(item_parsed))
                else:
                    result.append(str(item_parsed))
            except (ValueError, SyntaxError):
                result.append(item)
        else:
            result.append(str(item))
    return result


def count_events_per_admin_area(df):
    """
    Counts the number of Main_Events per Administrative_Area.

    Args:
        df (pd.DataFrame): DataFrame containing 'Main_Event' and 'Administrative_Areas_GeoJson' columns.
    Returns:
        pd.DataFrame: DataFrame with 'Administrative_Area' and 'Count' columns.
    """

    # Step 1: Extract administrative area identifiers into a new column
    def extract_admin_areas(area_list):
        if area_list is None or (isinstance(area_list, float) and np.isnan(area_list)):
            return []
        if not isinstance(area_list, list):
            area_list = [area_list]
        # Remove NaN values
        area_list = [item for item in area_list if not pd.isnull(item)]
        if not area_list:
            return []
        # Flatten and parse the list
        area_list = flatten_and_parse(area_list)
        return area_list

    # Check the data type of the column
    # print(type(df["Administrative_Areas_GeoJson"].iloc[0]))  # Check the first row to see the type of data

    df["Administrative_Areas"] = df["Administrative_Areas_GeoJson"].apply(extract_admin_areas)

    # Step 2: Explode the DataFrame so each administrative area has its own row
    df_exploded = df.explode("Administrative_Areas")

    # Step 3.2: Group by the administrative areas and count the number of unique Administrative_Areas
    event_count_per_admin_area = df_exploded.groupby("Administrative_Areas").size().reset_index(name="Count")
    # Step 4: Rename columns for clarity
    event_count_per_admin_area.columns = ["Administrative_Area", "Count"]

    return event_count_per_admin_area


import json

import geopandas as gpd
import jenkspy
import matplotlib.colors as mcolors


# world = gpd.read_file(f"/home/nl/Wikimpacts/Visualizations/earth_data/earth_data/earth_data/country_level/ne_110m_admin_0_countries.shp")
# visualize the spatial distribution using the Adminstrative_Areas column in L1
def plot_main_events_per_admin_area(df, geojson_file, country, event_count, output_file):
    """
    Plots the number of Main_Events per Administrative_Area based on the provided GeoJSON file.

    Args:
    df (pd.DataFrame): DataFrame containing the Main_Event and Administrative_Areas columns.
    geojson_file (str): Path to the GeoJSON file for the Administrative_Areas.
    output_file (str): Path where the plot will be saved.

    Returns:
    None: Saves the plot to the specified output file.
    """

    # Step 3: Prepare a dictionary to map Administrative_Areas names to their geometries (shapely polygons)
    Administrative_Areas_shapes = {}
    # Iterate over the DataFrame's 'Administrative_Areas_GeoJson' column
    # Iterate over 'Administrative_Areas_GeoJson' in 'sum' DataFrame
    # for gj_list in df["Administrative_Areas_GeoJson"]:
    for gj_list in df["Administrative_Areas_GeoJson"]:
        # Convert the string representation of the list into an actual list using ast.literal_eval
        try:
            items = ast.literal_eval(gj_list)
        except (ValueError, SyntaxError):
            # Skip this iteration if there is a parsing error
            continue
        # Ensure that 'items' is a list and iterate over its elements
        if isinstance(items, list):
            for gj in items:
                if gj:
                    gj = gj.strip().lower()  # Clean up the area name
                    # Check if 'gj' exists in the 'nid_to_geo_obj' dictionary
                    if gj in geojson_file:
                        # print(gj)
                        # Get the corresponding GeoJSON object
                        geo_obj = geojson_file[gj]
                        geo_obj_str = geo_obj.decode("utf-8")
                        # Step 2: Parse the string into a dictionary using json.loads
                        geo_obj_dict = json.loads(geo_obj_str)
                        # Step 3: Convert the dictionary to a Shapely object using shape()
                        geometry = shape(geo_obj_dict)
                        Administrative_Areas_shapes[gj] = geometry

    geometries = []
    area_names = []
    for area_name, geom in Administrative_Areas_shapes.items():
        geometries.append(geom)
        area_names.append(area_name)

    gdf = gpd.GeoDataFrame({"Administrative_Area": area_names, "geometry": geometries})

    # Merge with event counts
    merged_gdf = gdf.merge(event_count, on="Administrative_Area", how="left")

    # Replace NaN counts with zero
    merged_gdf["Count"] = merged_gdf["Count"].fillna(0)

    # Ensure 'Count' is numeric and finite
    merged_gdf["Count"] = pd.to_numeric(merged_gdf["Count"], errors="coerce")
    merged_gdf = merged_gdf[np.isfinite(merged_gdf["Count"])]

    breaks = jenkspy.jenks_breaks(merged_gdf["Count"].values, n_classes=6)
    # Ensure that zero is included as the first break
    if 0 not in breaks:
        breaks = np.insert(breaks, 0, 0)

    # Define colors, with light grey specifically for zero
    cmap_colors = [
        "#D3D3D3",  # Light grey for 0
        "#FEE0D2",  # Very pale red
        "#FCBBA1",  # Light salmon
        "#FC9272",  # Soft red
        "#FB6A4A",  # Strong red
        "#EF3B2C",  # Vivid red
        "#CB181D",  # Dark red
        "#99000D",  # Maroon
    ]

    # Adjust cmap_colors to ensure it matches the number of breaks
    # cmap_colors should have one less than the breaks if breaks include 0 explicitly
    if len(cmap_colors) != len(breaks) - 1:
        print("Warning: The number of colors in cmap_colors does not match the number of breaks.")
        cmap_colors = cmap_colors[: len(breaks) - 1]  # Trim or adjust as needed

    # Create colormap and norm for plotting
    cmap = mcolors.ListedColormap(cmap_colors)
    norm = mcolors.BoundaryNorm(breaks, cmap.N)

    # Plotting
    fig, ax = plt.subplots(figsize=(15, 10))
    world = gpd.read_file(country)
    world.plot(ax=ax, color="lightgray", edgecolor="gray", linewidth=0.5)

    # Plot using GeoPandas
    merged_gdf.plot(
        column="Count",
        cmap=cmap,
        norm=norm,
        linewidth=0.5,
        ax=ax,
        edgecolor="gray",
    )
    ax.grid(False)
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    plt.colorbar(sm, ax=ax, label=f"Number of Impact Data Point", shrink=0.5)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 90)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title(f"Spatial distribution of number of impact data points in country level in Wikimpacts 1.0 database ")
    plt.savefig(output_file, dpi=1200, bbox_inches="tight")
    plt.close
