import math
import pandas as pd
import geopandas as gpd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib.ticker as ticker

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
    scale: str = "viridis",
    highlight: list[str] = None,
    format_func: callable = None,
    log: bool = False,
    figsize: tuple[int, int] = (10, 10),
) -> px.choropleth:
    """
    Plots a choropleth map
    """
    df = df.copy(deep=True)
    df = df[df[color] != 0]
    if not ax:
        ax = plt.gca()

    legend = True
    if log:
        df[color] = df[color].apply(lambda x: x + math.e)
        df[color] = df[color].apply(lambda x: math.log(x, 10))
        legend = False
    # display(df[color])
    gpd.GeoDataFrame(df).plot(
        ax=ax,
        column=color,
        legend=legend,
        cmap="coolwarm",
        edgecolor="black",
        linewidth=0.75,
        legend_kwds={"shrink": 0.8},
        # norm=matplotlib.colors.LogNorm(vmin=1, vmax=df[color].max()),
    )

    if log:
        cbar = ax.get_figure().colorbar(ax.collections[0], ax=ax)
        cbar.set_ticks(
            [math.pow(x, 10) + math.e for x in [df[color].min(), df[color].max()]]
        )

    ax.set_axis_off()
    ax.set_title(title, fontweight="bold", fontsize=FONTSIZE)
    ax.ticklabel_format(style="plain")

    # if format_func:
    # plt.colorbar(, format=ticker.FuncFormatter(fmt))
    # ax.colorbar.set_major_formatter(ticker.FuncFormatter(format_func))

    if highlight:
        h = nbhd_df[nbhd_df["neighborhood"].isin(highlight)]
        h.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=2.5)
