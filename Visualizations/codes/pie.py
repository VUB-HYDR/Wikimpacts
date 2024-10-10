import matplotlib.pyplot as plt
import numpy as np


def plot_event_distribution_pie(df, custom_colors, title, output_file):
    # Calculate the event counts
    event_counts = df["Main_Event"].value_counts()
    event_labels = event_counts.index.tolist()
    data = event_counts.values  # Data for the pie chart

    # Generate a list of colors corresponding to the event types
    colors = [custom_colors[event] for event in event_labels]

    # Plot the pie chart
    fig, ax = plt.subplots(figsize=(20, 20), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(data, colors=colors, wedgeprops=dict(width=0.8), startangle=90)

    # Define properties for the labels
    kw = dict(
        arrowprops=dict(arrowstyle="-", lw=1.5, color="gray"),  # Using an arrow line style
        zorder=0,
        va="center",
        fontsize=25,
        fontweight="bold",
    )

    # Annotate each wedge with its label and percentage
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]

        connectionstyle = f"angle,angleA=0,angleB={ang},rad=30"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})

        percentage = f"{data[i] / sum(data) * 100:.1f}%"
        label_text = f"{event_labels[i]}\n{percentage}"

        x_text = 2.5 * np.sign(x)
        y_offset = 0.1 * (i - len(wedges) // 2)
        y_adjusted = y + y_offset

        ax.annotate(label_text, xy=(x, y), xytext=(x_text, y_adjusted), ha=horizontalalignment, **kw)

    # Set title and ensure the pie chart is drawn as a circle
    ax.set_title(title, fontsize=30, fontweight="bold", color="purple", loc="left", x=0, y=1.05)
    ax.set_aspect("equal")

    # Save the figure and show it
    plt.tight_layout()
    plt.savefig(output_file, format="pdf", dpi=1200, bbox_inches="tight", pad_inches=0.3)
    plt.close
