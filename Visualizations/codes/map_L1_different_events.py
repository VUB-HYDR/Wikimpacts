import ast
import json

import geopandas as gpd
import jenkspy
import matplotlib as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from shapely.geometry import shape

# map for each main event in L1


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


def count_events_per_admin_area(df, event):
    """
    Counts the number of Main_Events per Administrative_Area.

    Args:
        df (pd.DataFrame): DataFrame containing 'Main_Event' and 'Administrative_Areas_GeoJson' columns.
        event (str): The event type to filter on.

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

    df["Administrative_Areas"] = df["Administrative_Areas_GeoJson"].apply(extract_admin_areas)

    # Step 2: Explode the DataFrame so each administrative area has its own row
    df_exploded = df.explode("Administrative_Areas")

    # Step 3: Filter for the specific event and drop rows with NaN in "Administrative_Areas" or "Main_Event"
    df_exploded_filter = df_exploded[(df_exploded["Main_Event"] == event)]

    # Step 4: Group by the administrative areas and count the number of Main_Event occurrences
    event_count_per_admin_area = (
        df_exploded_filter.groupby("Administrative_Areas")["Main_Event"]
        .count()
        .reset_index()
        .rename(columns={"Administrative_Areas": "Administrative_Area", "Main_Event": "Count"})
    )

    # Step 5: Filter out non-finite values in the "Count" column
    event_count_per_admin_area = event_count_per_admin_area[np.isfinite(event_count_per_admin_area["Count"])]

    return event_count_per_admin_area


def get_explicit_color_gradient(base_color, n_shades):
    """
    Generate a color gradient from light to dark for the base color.
    """
    colors = ["#D3D3D3"]  # Light grey for zero or no data
    base_rgb = mcolors.to_rgb(base_color)

    # Generate gradient shades by scaling each RGB component
    gradient_colors = [
        mcolors.to_hex(
            (
                base_rgb[0] * (0.5 + 0.5 * i / n_shades),
                base_rgb[1] * (0.5 + 0.5 * i / n_shades),
                base_rgb[2] * (0.5 + 0.5 * i / n_shades),
            )
        )
        for i in range(1, n_shades + 1)
    ]

    colors.extend(gradient_colors[::-1])
    return colors


def plot_main_events_per_admin_area(df, country, geojson_file, custom_colors, event_count, output_file, event):
    # Prepare a dictionary to map Administrative_Areas names to their geometries
    Administrative_Areas_shapes = {}
    for gj_list in df["Administrative_Areas_GeoJson"]:
        try:
            items = ast.literal_eval(gj_list)
        except (ValueError, SyntaxError):
            continue
        if isinstance(items, list):
            for gj in items:
                if gj:
                    gj = gj.strip().lower()
                    if gj in geojson_file:
                        geo_obj = geojson_file[gj]
                        if isinstance(geo_obj, bytes):
                            geo_obj_str = geo_obj.decode("utf-8")
                        else:
                            geo_obj_str = geo_obj
                        geo_obj_dict = json.loads(geo_obj_str)
                        geometry = shape(geo_obj_dict)
                        if geometry.is_valid and not geometry.is_empty:
                            Administrative_Areas_shapes[gj] = geometry

    # Create a GeoDataFrame
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
    if merged_gdf.empty or merged_gdf["Count"].isnull().all() or (merged_gdf["Count"].sum() == 0):
        print(f"No data to plot for event: {event}. Skipping plot.")
        return

    # Calculate Jenks breaks only if data is sufficient
    unique_values_count = len(set(merged_gdf["Count"].values))
    n_classes = min(6, unique_values_count)

    if n_classes < 2:
        print(f"Insufficient data for Jenks breaks for event: {event}. Skipping plot.")
        return

    try:
        # Attempt to calculate Jenks breaks
        finite_breaks = jenkspy.jenks_breaks(merged_gdf["Count"].values, n_classes=n_classes)
    except Exception as e:
        print(f"Error calculating Jenks breaks for event: {event}. Error: {e}")
        return  # Exit if Jenks breaks calculation fails

    # Ensure finite_breaks has valid breaks and contains more than just zero
    if not finite_breaks or len(finite_breaks) < 2:
        print(f"No valid breaks generated for event: {event}. Skipping plot.")
        return

    # Proceed with finite breaks if available
    finite_breaks = [0] + [b for b in finite_breaks if b > 0]  # Ensure zero is the first break
    n_colors = len(finite_breaks) - 1  # Adjust number of colors based on valid breaks
    cmap_colors = get_explicit_color_gradient(custom_colors.get(event, "#0000FF"), n_colors)
    cmap = mcolors.ListedColormap(cmap_colors)
    norm = mcolors.BoundaryNorm(finite_breaks, ncolors=cmap.N)

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
    plt.colorbar(sm, ax=ax, label=f"Number of {event}", shrink=0.5)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 90)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title(f"Distribution of {event}")
    plt.savefig(output_file, dpi=1200, bbox_inches="tight")
    plt.close
