import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_decadal_event_distribution(df, custom_colors, title, output_file):
    # Convert 'Start_Date_Year' to numeric and drop NaN values
    df["Start_Date_Year"] = pd.to_numeric(df["Start_Date_Year"], errors="coerce")
    df = df.dropna(subset=["Start_Date_Year"])

    # Group years into decades
    df["Decade_Class"] = (df["Start_Date_Year"] // 10) * 10

    # Group by 'Decade_Class' and 'Main_Event', then count occurrences
    event_decade_counts = df.groupby(["Decade_Class", "Main_Event"]).size().reset_index(name="Count")

    # Pivot table to have one column per event type
    event_decade_counts_pivot = event_decade_counts.pivot(
        index="Decade_Class", columns="Main_Event", values="Count"
    ).fillna(0)

    # Ensure numeric values and sort columns by total count
    event_decade_counts_pivot = event_decade_counts_pivot.apply(pd.to_numeric, errors="coerce")
    event_totals = event_decade_counts_pivot.sum().sort_values(ascending=False)
    event_decade_counts_pivot = event_decade_counts_pivot[event_totals.index]

    # Calculate total events per decade
    totals_per_decade = event_decade_counts_pivot.sum(axis=1)

    # Plot the grouped bar chart
    fig, ax = plt.subplots(figsize=(10, 8))
    event_decade_counts_pivot.plot(
        kind="bar",
        stacked=True,
        color=[custom_colors.get(event, "#333333") for event in event_decade_counts_pivot.columns],
        ax=ax,
        legend=False,
    )

    # Hide the grid
    ax.grid(False)

    # Add data labels with percentages
    for p in ax.patches:
        width = p.get_width()
        height = p.get_height()
        x = p.get_x() + width / 2
        y = p.get_y() + height / 2
        if height > 0:
            ax.text(x, y, f"{height:.0f}", ha="center", va="center", fontsize=10, color="white")

    # Customize the x-axis labels
    ax.set_xticklabels([f"{int(decade)}s" for decade in event_decade_counts_pivot.index], rotation=45, fontsize=12)

    # Set y-axis limits and labels
    max_y = int(totals_per_decade.max()) + 2
    plt.yticks(np.arange(0, max_y + 1, 2), fontsize=12)

    # Add labels and title
    plt.xlabel("Decade", fontsize=14)
    plt.ylabel("Number of events", fontsize=14)
    plt.title(title, fontsize=16)

    # Add a legend
    ax.legend(event_decade_counts_pivot.columns, loc="upper left", bbox_to_anchor=(1.05, 1), fontsize=10)

    # Adjust layout for the legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    # Save the figure
    plt.savefig(output_file, format="pdf", dpi=600)
    plt.close
