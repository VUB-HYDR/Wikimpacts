# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:39:59 2024
@author: Paul Muñoz (paul.munoz@vub.be) + Ni Li
"""

import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set Seaborn aesthetics
sns.set(style="whitegrid")
# Set font style and size globally
plt.rcParams.update({"font.family": "Arial", "font.size": 12})

db_path = f"/home/nl/Wikimpacts/impact_slim.v1.db"
# Connect to the SQLite database
conn = sqlite3.connect(db_path)
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
df = tables_data["Total_Summary"]
# Define custom colors for each event
custom_colors = {
    "Flood": "#1f77b4",  # blue
    "Drought": "#ff7f0e",  # orange
    "Wildfire": "#d62728",  # red
    "Tornado": "#9467bd",  # purple
    "Extratropical Storm/Cyclone": "#2ca02c",  # green
    "Tropical Storm/Cyclone": "#bcbd22",  # yellow-green
    "Extreme Temperature": "#e377c2",  # pink
}
#####################################################################################
####################################################################################
# Calculate the event counts
event_counts = df["Main_Event"].value_counts()

# Generate a list of colors corresponding to the event types
colors = [custom_colors[event] for event in event_counts.index]

# Create a pie chart using Matplotlib with the custom colors, with Seaborn styling
plt.figure(figsize=(4, 4))
wedges, texts, autotexts = plt.pie(
    event_counts,
    labels=None,  # Remove default labels
    colors=colors,
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops=dict(width=0.3),
)

for autotext, color in zip(autotexts, colors):
    autotext.set_color(color)
    autotext.set_text("")  # Clear the autopct percentage to avoid duplicate display
# Add the title in the center of the wheel
plt.text(0, 0, "Distribution of Events by Type", ha="center", va="center", fontsize=12, color="black")
# Equal aspect ratio ensures that pie is drawn as a circle
plt.axis("equal")
plt.tight_layout()
output_path = "distribution of events by type(pie).png"
plt.savefig(output_path, format="png", dpi=600)
plt.show()
###############
#############


# Create a traditional pie chart (no "donut" hole)
plt.figure(figsize=(4, 4))
wedges, texts, autotexts = plt.pie(
    event_counts,
    labels=None,  # Remove default labels
    colors=colors,
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops=dict(width=1.0),  # Set width to 1.0 to make it a traditional pie
)

# Change the color of the percentage texts to match the pie slice colors
for autotext, color in zip(autotexts, colors):
    autotext.set_color(color)
    autotext.set_text("")  # Clear the autopct percentage to avoid duplicate display

# Add a title at the top of the chart (not in the center)
# Equal aspect ratio ensures that pie is drawn as a circle
plt.axis("equal")
# Save the figure as PNG (optional line, comment it out if not needed)
# plt.savefig(output_path, format='png', dpi=600)
# Show the pie chart
plt.tight_layout()
output_path = "distribution of events by type(pie).png"
plt.savefig(output_path, format="png", dpi=600)
plt.show()

#####################################################################################
####################################################################################

# Convert 'Start_Date_Year' to numeric
df["Start_Date_Year"] = pd.to_numeric(df["Start_Date_Year"], errors="coerce")
# Drop rows where 'Start_Date_Year' is NaN
df = df.dropna(subset=["Start_Date_Year"])
# Group the years into decades (e.g., 2020 for 2020s, 2010 for 2010s)
df["Decade_Class"] = (df["Start_Date_Year"] // 10) * 10
# Group by 'Decade_Class' and 'Main_Event' and count occurrences
event_decade_counts = df.groupby(["Decade_Class", "Main_Event"]).size().reset_index(name="Count")
# Pivot the table to have one column per event type
event_decade_counts_pivot = event_decade_counts.pivot(
    index="Decade_Class", columns="Main_Event", values="Count"
).fillna(0)
# Ensure that all values in event_decade_counts_pivot are numeric
event_decade_counts_pivot = event_decade_counts_pivot.apply(pd.to_numeric, errors="coerce")
# Calculate the total number of events in each decade
totals_per_decade = event_decade_counts_pivot.sum(axis=1)
# Sort the columns so the most frequent event type (Tropical Storm/Cyclone) appears first
event_totals = event_decade_counts_pivot.sum().sort_values(ascending=False)
event_decade_counts_pivot = event_decade_counts_pivot[event_totals.index]  # Reorder columns based on total counts
# Plot grouped bar chart using Seaborn settings for aesthetics, with Matplotlib for stacking
fig, ax = plt.subplots(figsize=(12, 8))
bars = event_decade_counts_pivot.plot(
    kind="bar",
    stacked=True,
    color=[custom_colors.get(event, "#333333") for event in event_decade_counts_pivot.columns],
    ax=ax,
)
# Add data labels with percentages on each bar (rounded to 1 decimal)
for p in ax.patches:
    width = p.get_width()  # Get the width of the bar
    height = p.get_height()  # Get the height (value) of the bar
    decade_label = int(p.get_x() + p.get_width() / 2)  # Calculate the correct decade
    if height > 0:  # Only display if there's a non-zero height
        total = totals_per_decade.iloc[decade_label]  # Access the total for the correct decade
        percentage = np.round((height / total) * 100, 1)  # Calculate percentage

        # Annotate the percentage in the middle of the segment
        ax.annotate(
            f"{percentage}%",  # Format percentage with 1 decimal
            (p.get_x() + width / 2.0, p.get_y() + height / 2.0),  # Position label in the middle
            ha="center",
            va="center",
            fontsize=10,
            color="black",
        )
# Rotate x-axis labels for better readability and set custom decade labels
decade_labels = [
    f"{int(decade)}s" for decade in event_decade_counts_pivot.index
]  # Custom decade labels as 2020s, 2010s, etc.
ax.set_xticklabels(decade_labels, rotation=45, fontsize=16)
# Set y-axis ticks to increase by 2
max_y = int(totals_per_decade.max()) + 2  # Set y limit based on the max number of events, rounded up
plt.yticks(np.arange(0, max_y + 1, 2), fontsize=16)  # Set ticks every 2 units
# Add labels and title
plt.xlabel("Decade", fontsize=16)
plt.ylabel("Number of events", fontsize=16)
plt.title("Decadal occurrence of events by type", fontsize=16)
# Adjust the legend
plt.legend(title="Event type", fontsize=16, title_fontsize=16)
# Adjust the layout
plt.tight_layout()
output_path = "Decadal occurrence of events by type(percentages).png"
plt.savefig(output_path, format="png", dpi=600)
# Show the plot
plt.show()
#################################################################
####################################################################################
# read other table
# Relevant columns in Total_Summary for different impacts
impact_columns = [
    "Total_Deaths_Max",
    "Total_Injuries_Max",
    "Total_Affected_Max",
    "Total_Displaced_Max",
    "Total_Homeless_Max",
    "Total_Buildings_Damaged_Max",
]

# Define event types you want to analyze
event_types = df_summary["Main_Event"].unique()  # Get unique event types

# Dictionary to store sums for each event type
event_impact_sums = {}

for column in impact_columns:
    df_summary[column] = pd.to_numeric(df_summary[column], errors="coerce")

# Loop through each event type and sum the relevant columns
for event_type in event_types:
    # Filter rows for the given event type
    event_data = df_summary[df_summary["Main_Event"] == event_type]

    # Sum up the relevant columns
    impact_sums = event_data[impact_columns].sum()

    # Store the results in the dictionary
    event_impact_sums[event_type] = impact_sums

# Convert the dictionary to a DataFrame for easier visualization
impact_sums_df = pd.DataFrame(event_impact_sums).T  # Transpose to have event types as rows


# Plot the results for Floods
flood_impact_sums = impact_sums_df.loc["Flood"]  # Replace 'Flood' with any other event type if needed

# Create a bar chart for the Flood event with log scale for y-axis
plt.figure(figsize=(10, 6))

# Plot the bar chart using Seaborn
sns.barplot(x=flood_impact_sums.index, y=flood_impact_sums.values, palette="viridis")

# Set the y-axis to log scale
plt.yscale("log")

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Add labels and title
plt.xlabel("Impact Type", fontsize=12)
plt.ylabel("Total Max Value (Log Scale)", fontsize=12)
plt.title("Total Max Impact for Flood Events (Log Scale)", fontsize=14)

# Adjust the layout
plt.tight_layout()

# Show the plot
plt.show()

###################
###############
########################
# Define impact categories
numerical_impacts = [
    "Total_Deaths_Max",
    "Total_Injuries_Max",
    "Total_Affected_Max",
    "Total_Displaced_Max",
    "Total_Homeless_Max",
    "Total_Buildings_Damaged_Max",
]
monetary_impacts = ["Total_Damage_Max", "Total_Insured_Damage_Max"]
# Set up the color scheme: one for numerical impacts and one for monetary impacts
numerical_color = "#4b0082"  # Pastel Blue
monetary_color = "#32cd32"  # Pastel Green

# Define colors based on impact types
impact_colors = [numerical_color] * len(numerical_impacts) + [monetary_color] * len(monetary_impacts)
# Define custom x-tick labels
xtick_labels = {
    "Total_Deaths_Max": "Deaths",
    "Total_Injuries_Max": "Injuries",
    "Total_Affected_Max": "Affected",
    "Total_Displaced_Max": "Displaced",
    "Total_Homeless_Max": "Homeless",
    "Total_Buildings_Damaged_Max": "Buildings Damaged",
    "Total_Damage_Max": "Total Damage",
    "Total_Insured_Damage_Max": "Insured Damage",
}
# Set the number of columns (3 events per row)
ncols = 3
nrows = 3  # Set the number of rows
# Set up the figure and axes for subplots (multiple rows, 3 subplots per row)
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 5, nrows * 5), sharey=False)
# Flatten the axes array to make it easier to iterate
axes = axes.flatten()
# Convert relevant columns to numeric, coercing errors to NaN, then fill NaN with 0
for column in numerical_impacts + monetary_impacts:
    df_summary[column] = pd.to_numeric(df_summary[column], errors="coerce").fillna(0)
# Loop through each event type and plot the impact data in a separate subplot
for i, event_type in enumerate(selected_event_types):
    # Filter rows for the given event type
    event_data = df_summary[df_summary["Main_Event"] == event_type]
    # Sum up the relevant columns
    impact_sums = event_data[numerical_impacts + monetary_impacts].sum()
    # Create a bar chart for the current event with specific colors for numerical and monetary impacts
    sns.barplot(x=impact_sums.index, y=impact_sums.values, palette=impact_colors, ax=axes[i])
    # Set log scale for y-axis
    axes[i].set_yscale("log")
    # Apply the custom x-tick labels using the dictionary
    new_labels = [xtick_labels[label] for label in impact_sums.index]
    axes[i].set_xticklabels(new_labels, rotation=90, fontsize=14)
    # Set the title for each subplot
    axes[i].set_title(f"{event_type} Impacts", fontsize=14)
    # Only show y-axis labels for the first column of each row
    if i % ncols == 0:
        axes[i].set_ylabel("Total Max Value (Log Scale)", fontsize=14)
    else:
        axes[i].set_ylabel("")
    # Auto-adjust y-axis to fit the data
    axes[i].set_ylim(0.1, impact_sums.max() * 1.2)  # Adjust to have some space above the highest value
# Hide any unused subplots if the number of events isn't a multiple of 3
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])  # Remove the unused axes
# Set overall plot labels
fig.suptitle("Total Max Impact for Different Main Events (Log Scale)", fontsize=16)
# Add a legend to differentiate numerical and monetary impacts (in 2 rows next to the last row plot)
handles = [
    plt.Rectangle((0, 0), 1, 1, color=numerical_color, label="Numerical Impact"),
    plt.Rectangle((0, 0), 1, 1, color=monetary_color, label="Monetary Impact"),
]
fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.5, 0.2), ncol=1, fontsize=14)
# Adjust the layout
plt.tight_layout(rect=[0, 0, 1, 0.96])
output_path = "Total_impacts_per_event.png"
plt.savefig(output_path, format="png", dpi=600)
# Show the plot
plt.show()
###############################################################################
###############################################################################
###############################################################################

# ALTERNATIVE
# Custom x-tick labels as a dictionary
xtick_labels = {
    "Total_Deaths_Max": "Deaths",
    "Total_Injuries_Max": "Injuries",
    "Total_Affected_Max": "Affected",
    "Total_Displaced_Max": "Displaced",
    "Total_Homeless_Max": "Homeless",
    "Total_Buildings_Damaged_Max": "Buildings Damaged",
    "Total_Damage_Max": "Total Damage",
    "Total_Insured_Damage_Max": "Insured Damage",
}

impact_columns = [
    "Total_Deaths_Max",
    "Total_Injuries_Max",
    "Total_Affected_Max",
    "Total_Displaced_Max",
    "Total_Homeless_Max",
    "Total_Buildings_Damaged_Max",
    "Total_Damage_Max",
    "Total_Insured_Damage_Max",
]

# Set up colors for each event type based on custom colors
event_colors = [custom_colors[event] for event in selected_event_types]
# Convert relevant columns to numeric, coercing errors to NaN, then fill NaN with 0
for column in impact_columns:
    df_summary[column] = pd.to_numeric(df_summary[column], errors="coerce").fillna(0)
# Loop through each event type to sum impacts and prepare data for bubble chart
bubble_data = []
for i, event_type in enumerate(selected_event_types):
    event_data = df_summary[df_summary["Main_Event"] == event_type]
    impact_sums = event_data[impact_columns].sum()
    for impact, value in impact_sums.items():
        bubble_data.append(
            {
                "Impact": xtick_labels.get(impact, impact),  # Custom x-tick labels
                "Event": event_type,
                "Impact_Sum": value,
                "Color": custom_colors[event_type],  # Apply custom color to each event type
                "Size": value,  # Bubble size is proportional to the impact sum
            }
        )

# Convert bubble_data to a DataFrame for easier plotting
# Convert bubble_data to a DataFrame for easier plotting
bubble_df = pd.DataFrame(bubble_data)

# Use log of the impact sums to better visualize bubble size differences
bubble_df["Log_Size"] = np.log10(bubble_df["Size"] + 1) * 400  # Add 1 to avoid log(0)

# Create the bubble chart with better scaling
plt.figure(figsize=(12, 12))
sc = plt.scatter(
    x=bubble_df["Impact"],
    y=bubble_df["Event"],
    s=bubble_df["Log_Size"] * 1.2,  # Increased scaling for better separation
    c=bubble_df["Color"],
    alpha=0.6,
    edgecolor="w",
    linewidth=1,
)

# Set labels and title with fontsize 14
plt.xlabel("Impact Type", fontsize=14)
plt.ylabel("Main Event", fontsize=14)
plt.title("Bubble Chart of Total Max Impact by Main Event and Impact Type (Log Scale)", fontsize=16)

# Rotate x-axis labels for readability, and set their fontsize to 14
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

# Adjust legend to show specific size examples
# Define the specific values you'd like to display in the legend
legend_values = [1e3, 1e5, 1e7, 1e9, 1e11]  # Example: customize values for legend
legend_labels = [f"{int(value):,}" for value in legend_values]  # Format with thousands separator

# Plot circles to represent sizes in the legend
for value, label in zip(legend_values, legend_labels):
    plt.scatter([], [], s=np.log10(value + 1) * 400, c="gray", alpha=0.6, edgecolor="w", label=label)

# Customize and move the legend to the bottom center with more rows
plt.legend(
    title="Impact Size (Log Scale)",
    fontsize=14,  # Legend fontsize
    title_fontsize=14,  # Legend title fontsize
    loc="lower center",
    bbox_to_anchor=(0.5, -0.35),  # Adjust this to move it further down
    ncol=5,  # Number of columns in the legend
)
output_path = "Total_impacts_per_event_bubble.png"
plt.savefig(output_path, format="png", dpi=600)
# Show the plot with tight layout
plt.tight_layout()
plt.show()
