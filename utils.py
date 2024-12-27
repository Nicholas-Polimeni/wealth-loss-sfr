import math
from matplotlib import patches
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors

FONTSIZE = 13


def area_plot(
    df: pd.DataFrame,
    x: str,
    cols: list[str],
    labels: list[str],
    x_label: str = None,
    y_label: str = None,
    title: str = None,
    ax: plt.Axes = None,
    legend: dict = None,
    theme: str = "darkgrid",
    palette: str = "Set2",
    ticks: bool = True,
    line_weight: float = 1.45,
    opacity: float = 0.25,
    format_func: callable = None,
    format_tuple: tuple = None,
    ann: str = None,
) -> plt.Figure:
    """
    Plots an area linegraph
    """

    if not ax:
        ax = plt.gca()

    sns.set_theme(style=theme)
    palette = sns.color_palette(palette)

    for i, col in enumerate(cols):
        sns.lineplot(
            data=df,
            x=x,
            y=col,
            label=labels[i],
            ax=ax,
            lw=line_weight,
        )
        ax.fill_between(df[x], 0, df[col], alpha=opacity)

        if ann:
            for x_value, y_value, write in zip(df[x][::2], df[col][::2], df[ann][::2]):
                ax.text(
                    x_value,
                    y_value + 0.01,
                    f"~{round(write, -2) // 1000}K",
                    ha="center",
                    va="bottom",
                )

    if x_label:
        ax.set_xlabel(x_label, fontweight="bold")
    else:
        ax.set_xlabel("")

    if y_label:
        ax.set_ylabel(y_label, fontweight="bold")
    else:
        ax.set_ylabel("")

    if format_tuple and format_tuple[0]:
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
    if format_tuple and format_tuple[1]:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))

    if title:
        ax.set_title(title, fontweight="bold", fontsize=FONTSIZE)

    if not ticks:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    if isinstance(legend, dict):
        ax.legend(**legend)
    elif legend:
        ax.legend()
    else:
        ax.get_legend().remove()


def stacked_plot(
    df: pd.DataFrame,
    x: str,
    cols: list[str],
    labels: list[str],
    x_label: str = None,
    y_label: str = None,
    title: str = None,
    ax: plt.Axes = None,
    legend: dict = None,
    theme: str = "darkgrid",
    palette: str = "Set2",
    ticks: bool = True,
    line_weight: float = 1,
    opacity: float = 0.2,
    format_func: callable = None,
    format_tuple: tuple = None,
) -> plt.Figure:
    """
    Plots an area linegraph
    """
    if not ax:
        ax = plt.gca()

    sns.set_theme(style=theme)
    palette = sns.color_palette(palette)

    ax.stackplot(df[x], df[cols].T, labels=labels, alpha=opacity)

    if x_label:
        ax.set_xlabel(x_label, fontweight="bold")
    else:
        ax.set_xlabel("")

    if y_label:
        ax.set_ylabel(y_label, fontweight="bold")
    else:
        ax.set_ylabel("")

    if title:
        ax.set_title(title, fontweight="bold", fontsize=FONTSIZE)

    if not ticks:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    if format_tuple and format_tuple[0]:
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_func))
    if format_tuple and format_tuple[1]:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))

    if isinstance(legend, dict):
        ax.legend(**legend)
    elif legend:
        ax.legend()
    else:
        ax.get_legend().remove()


def map(
    df: gpd.GeoDataFrame,
    color: str,
    title: str,
    nbhd_df: gpd.GeoDataFrame = None,
    ax: plt.Axes = None,
    highlight: list[str] = None,
    format_func: callable = None,
    log: bool = False,
    legend: bool = True,
) -> px.choropleth:
    """
    Plots a choropleth map
    """
    df = df.copy(deep=True)
    df = df[df[color] != 0]
    if not ax:
        ax = plt.gca()

    norm = None
    if log:
        norm = mcolors.LogNorm(vmin=df[color].min(), vmax=df[color].max())

    if log:
        df[f"log_{color}"] = np.log(df[color])
        color = f"log_{color}"

    # display(df[color])
    gpd.GeoDataFrame(df).plot(
        ax=ax,
        column=color,
        legend=False,
        cmap="coolwarm",
        edgecolor="black",
        linewidth=0.75,
    )
    nbhd_df.plot(
        ax=ax, facecolor="none", legend=False, edgecolor="black", linewidth=0.75
    )

    ax.set_axis_off()
    ax.set_title(title, fontweight="bold", fontsize=FONTSIZE)
    ax.title.set_position([0.58, 1.05])
    ax.ticklabel_format(style="plain")

    if log:

        def log_tick_formatter(val, pos=None):
            if color == "total_loss_adj":
                return str(f"{round((round(np.exp(val), 3) / 1000000), 2)}M")
            else:
                return str(round(np.exp(val), 3))

        # can't have 0s
        cbar = ax.get_figure().colorbar(mappable=ax.collections[0], ax=ax, shrink=0.8)
        cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(log_tick_formatter))
    else:
        cbar = ax.get_figure().colorbar(ax.collections[0], ax=ax, shrink=0.8)

    if format_func and not log:
        cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))

    color = color.replace("log_", "")
    highlight_nbhds = pd.DataFrame(
        df.sort_values(by=color, ascending=False).head(3)["neighborhood"]
    )

    if highlight:
        h = gpd.GeoDataFrame(highlight_nbhds.merge(nbhd_df, on="neighborhood"))
        h = h.set_geometry("geometry")
        h = h.set_crs(epsg=4326)

        h.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=1.75)

        # Add nums in highlighted areas and store geometry
        legend_data = {}
        count = 1
        for i, row in h.iterrows():
            ax.annotate(
                text=str(count),
                xy=(row["geometry"].centroid.x, row["geometry"].centroid.y),
                horizontalalignment="center",
                verticalalignment="center",
                bbox=dict(
                    boxstyle="circle,pad=0.05", facecolor="white", edgecolor="none"
                ),
            )
            # legend_data.append((count, row["neighborhood"], row["geometry"]))
            legend_data.update({count: row["neighborhood"]})
            count += 1

        # Add custom annotations for neighborhoods
        y_offset = 0.05
        ax.annotate(
            text=f"Top 3 Neighborhoods",
            xy=(0.5, -0.05),
            xycoords="axes fraction",
            fontsize=12,
            fontweight="bold",
            ha="center",
        )
        for i, name in legend_data.items():
            x = 0.5
            y = -0.05 - (y_offset * i)
            if format_func:
                val = format_func(float(df[df["neighborhood"] == name][color]), 0)
            else:
                val = round(float(df[df["neighborhood"] == name][color]), 3)
            ax.annotate(
                text=",".join(f"{i}: {name}".split(",")[:2]) + f" ({val})",
                xy=(x, y),
                xycoords="axes fraction",
                fontsize=12,
                ha="center",
            )

            # init_x, init_y = geometry.exterior.xy
            # # calculate distance between annotation and original geometry
            # x_diff = x - init_x[0]
            # y_diff = y - init_y[0]
            # # subtract distance from init geometry to move it to the new position
            # new_x = init_x - x_diff
            # new_y = init_y - y_diff
            # plt.plot(new_x, y, color="gray", linewidth=0.8)

        # # Initialize a list to store your mini axes for legend items
        # legend_items = []

        # # Iterate through your selected neighborhoods
        # for idx, row in nbhd_df[nbhd_df["neighborhood"].isin(highlight)].iterrows():
        #     # Create a new figure and axis for each neighborhood shape
        #     fig_legend, ax_legend = plt.subplots()
        #     # Plot the neighborhood shape on this mini axis
        #     nbhd_df[nbhd_df["neighborhood"] == row["neighborhood"]].plot(ax=ax_legend)
        #     ax_legend.axis("off")  # Hide axis lines and labels

        #     # Convert this mini plot to an image (as used in a legend)
        #     fig_legend.canvas.draw()  # Render the figure
        #     image = np.frombuffer(fig_legend.canvas.tostring_rgb(), dtype="uint8")
        #     image = image.reshape(fig_legend.canvas.get_width_height()[::-1] + (3,))
        #     plt.close(fig_legend)  # Close the figure to save memory

        #     # Create an OffsetImage object for the mini plot
        #     im = OffsetImage(image, zoom=0.2)  # Adjust zoom as needed
        #     # Create an AnnotationBbox for each mini plot
        #     ab = AnnotationBbox(
        #         im,
        #         (0.5, -0.5),
        #         frameon=False,
        #         xycoords="axes fraction",
        #         arrowprops=dict(arrowstyle="->"),
        #     )
        #     # Add the AnnotationBbox to the legend_items list
        #     legend_items.append((ab, row["neighborhood"]))

        # # Place each mini plot next to the map, acting as a legend entry
        # for i, (item, label) in enumerate(legend_items):
        #     # Positioning each mini plot on the main figure
        #     ax.annotate(
        #         label,
        #         xy=(0.25, i * 0.1),
        #         xycoords="axes fraction",
        #         xytext=(15, 0),
        #         textcoords="offset points",
        #         va="center",
        #     )
        #     ax.add_artist(item)


def map_select(
    df: gpd.GeoDataFrame,
    color: str,
    title: str,
    nbhd_df: gpd.GeoDataFrame = None,
    ax: plt.Axes = None,
    highlight: list[str] = None,
    format_func: callable = None,
    log: bool = False,
    legend: bool = False,
) -> px.choropleth:
    """
    Plots a choropleth map
    """
    df = df.copy(deep=True)
    df = df[df[color] != 0]
    if not ax:
        ax = plt.gca()

    norm = None
    # if log:
    #    norm = mcolors.LogNorm(vmin=df[color].min(), vmax=df[color].max())

    if log:
        df[f"log_{color}"] = np.log(df[color])
        color = f"log_{color}"

    # display(df[color])
    gpd.GeoDataFrame(df).plot(
        ax=ax,
        column=color,
        legend=False,
        cmap="coolwarm",
        edgecolor="black",
        linewidth=0.75,
    )
    nbhd_df.plot(
        ax=ax, facecolor="none", legend=False, edgecolor="black", linewidth=0.75
    )

    ax.set_axis_off()
    ax.set_title(title, fontweight="bold", fontsize=FONTSIZE)
    ax.title.set_position([0.58, 1.05])
    ax.ticklabel_format(style="plain")

    if log:

        def log_tick_formatter(val, pos=None):
            return str(round(np.exp(val), 3))

        # can't have 0s
        cbar = ax.get_figure().colorbar(mappable=ax.collections[0], ax=ax, shrink=0.8)
        cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(log_tick_formatter))
    else:
        cbar = ax.get_figure().colorbar(ax.collections[0], ax=ax, shrink=0.8)

    if format_func:
        cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))

    color = color.replace("log_", "")
    if highlight == "true":
        highlight_nbhds = pd.DataFrame(
            df.sort_values(by=color, ascending=False).head(3)["neighborhood"]
        )
    elif highlight:
        highlight_nbhds = pd.DataFrame(
            df[df["neighborhood"].isin(highlight)].drop(columns=["geometry"])
        )
    else:
        return

    if highlight:
        h = gpd.GeoDataFrame(highlight_nbhds.merge(nbhd_df, on="neighborhood"))
        h = h.set_geometry("geometry")
        h = h.set_crs(epsg=4326)

        h.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=1.75)

        # Add nums in highlighted areas and store geometry
        legend_data = {}
        count = 1
        for i, row in h.iterrows():
            ax.annotate(
                text=str(count),
                xy=(row["geometry"].centroid.x, row["geometry"].centroid.y),
                horizontalalignment="center",
                verticalalignment="center",
                bbox=dict(
                    boxstyle="circle,pad=0.0", facecolor="white", edgecolor="none"
                ),
            )
            # legend_data.append((count, row["neighborhood"], row["geometry"]))
            legend_data.update({count: row["neighborhood"]})
            count += 1

        # Add custom annotations for neighborhoods
        y_offset = 0.05
        if legend:
            ax.annotate(
                text=legend,
                xy=(0.5, -0.05),
                xycoords="axes fraction",
                fontsize=12,
                fontweight="bold",
                ha="center",
            )
        for i, name in legend_data.items():
            x = 0.5
            y = -0.05 - (y_offset * i)
            ax.annotate(
                text=",".join(f"{i}: {name}".split(",")[:2])
                + f" ({round(float(df[df['neighborhood'] == name][color]), 3):,})",
                xy=(x, y),
                xycoords="axes fraction",
                fontsize=12,
                ha="center",
            )
