import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd


def filter_and_save_dataframes(df, target_columns):
    filter_ed = df[
        (df["Start Year"] < 2024)
        | ((df["Start Year"] == 2024) & (df["Start Month"] < 2))
        | ((df["Start Year"] == 2024) & (df["Start Month"] == 2) & (df["Start Day"] < 29))
    ]

    resulting_dfs = {}

    # Loop through each column and create a new DataFrame where the column value is not None/NaN
    for column in target_columns:
        filtered_df = filter_ed[filter_ed[column].notna()].copy()
        # Generate a DataFrame name from the column name
        df_name = column.lower().replace(" ", "_").replace("('000_us$)", "").replace(".", "").replace(",", "")
        resulting_dfs[df_name] = filtered_df

    # Append all filtered DataFrames together
    appended_df = pd.concat(resulting_dfs.values(), ignore_index=True)

    return resulting_dfs, appended_df


def plot_emdat(df, country, output_file):
    # Load world GeoDataFrame
    world = gpd.read_file(country)

    # Merge world with appended_df on ISO code
    iso_column_name = "ADM0_A3"
    merged = world.merge(df, left_on=iso_column_name, right_on="ISO", how="left")

    # Count the frequency of each ISO code
    iso_frequency = df["ISO"].value_counts()

    # Add frequency to merged GeoDataFrame
    merged["frequency"] = merged[iso_column_name].map(iso_frequency).fillna(0)

    # Define custom breaks
    breaks = [0, 1, 250, 500, 1000, 1500, 2000, 3127]

    # Classify frequencies based on custom breaks
    def classify_frequency(value, breaks):
        for i in range(1, len(breaks)):
            if breaks[i - 1] <= value < breaks[i]:
                return i - 1
        return len(breaks) - 2

    merged["frequency_class"] = merged["frequency"].apply(lambda x: classify_frequency(x, breaks))

    # Define the custom colormap

    cmap_colors = [
        "#D3D3D3",  # Light grey for 0
        "#FEE0D2",  # Very pale red
        "#FC9272",  # Soft red
        "#FB6A4A",  # Strong red
        "#EF3B2C",  # Vivid red
        "#CB181D",  # Dark red
        "#99000D",  # Maroon
    ]

    cmap = mcolors.ListedColormap(cmap_colors)
    norm = mcolors.BoundaryNorm(boundaries=breaks, ncolors=len(cmap_colors))

    # Plotting the world map with merged data
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))

    # Plotting the merged GeoDataFrame with correct column and colormap
    # merged.plot(column='frequency', ax=ax, legend=True, cmap=cmap, norm=norm, edgecolor='gray',linewidth=0.5)

    merged.plot(column="frequency", ax=ax, cmap=cmap, norm=norm, edgecolor="gray", linewidth=0.5)

    # Add color bar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []  # Required for ScalarMappable to work
    cbar = fig.colorbar(sm, ax=ax, shrink=0.58)
    cbar.set_label("Number of Impact Data Points")

    # Add title and show plot
    plt.title("Spatial distribution of impact data points in country level in EM-DAT database")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 90)
    ax.set_xticks([])
    ax.set_yticks([])

    plt.savefig(output_file, dpi=1200, bbox_inches="tight")
    plt.close
