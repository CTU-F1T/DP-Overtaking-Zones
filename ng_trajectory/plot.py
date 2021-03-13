#!/usr/bin/env python3.6
# plot.py
"""Plot functions for ng_trajectory.
"""
######################
# Imports & Globals
######################

import numpy
    

try:
    from ng_trajectory import matplotlib, pyplot
except:
    pass

from ng_trajectory import PLOT_AVAILABLE

from typing import List


######################
# Decorators
######################

def plot_only(f):
    """Decorator for disabling plotting functions."""
    global PLOT_AVAILABLE

    def block(*args, **kwargs):
        return lambda *x, **y: None

    def let_pass(*args, **kwargs):
        return f(*args, **kwargs)

    return let_pass if PLOT_AVAILABLE else block


######################
# Figures
######################

@plot_only
def figureCreate() -> matplotlib.figure.Figure:
    """Create a figure with export preset."""
    figure = pyplot.figure(dpi=300)
    figure.add_subplot(111)
    return figure


@plot_only
def axisEqual(figure: matplotlib.figure.Figure = None) -> None:
    """Equal axis on current / selected figure."""
    if figure is None:
        figure = pyplot.gcf()

    figure.axes[0].axis("equal")


@plot_only
def figureSave(filename: str, figure: matplotlib.figure.Figure = None) -> None:
    """Save figure into a file."""
    if figure is None:
        figure = pyplot.gcf()

    figure.savefig(filename, bbox_inches="tight", dpi=300, pad_inches=0)


@plot_only
def figureShow() -> None:
    """Show figure to the user."""
    pyplot.show()


######################
# Type plot functions
######################

def trackPlot(track: numpy.ndarray, figure: matplotlib.figure.Figure = None) -> None:
    """Plot a track to selected figure.

    Arguments:
    track -- points of the track valid area, nx2 numpy.ndarray
    figure -- figure to plot to, matplotlib.figure.Figure, default 'current figure'
    """
    pointsScatter(track, figure, s=1, color="gray")


def bordersPlot(borders: List[numpy.ndarray], colored: bool = True, figure: matplotlib.figure.Figure = None) -> None:
    """Plot borders of the segments to a selected figure.

    Arguments:
    borders -- border points of the groups, n-list of x2 numpy.ndarray
    colored -- when True, plot is done colored, otherwise single color, bool, default True
    figure -- figure to plot to, matplotlib.figure.Figure, default 'current figure'
    """
    if colored:
        #groupsScatter(borders, figure, s=1)
        groupsPlot(borders, figure, linewidth=0.6, linestyle="dotted")
    else:
        #groupsScatter(borders, figure, s=1, color="gray")
        groupsPlot(borders, figure, linewidth=0.6, linestyle="dotted", color="gray")


######################
# General functions
######################

@plot_only
def pointsScatter(points: numpy.ndarray, figure: matplotlib.figure.Figure = None, **kwargs) -> None:
    """Scatter points.

    Arguments:
    points -- points to be scattered, nx(>=2) numpy.ndarray
    **kwargs -- keyword arguments to be passed to scatter
    """
    if figure is None:
        figure = pyplot.gcf()

    figure.axes[0].scatter(points[:, 0], points[:, 1], **kwargs)


@plot_only
def pointsPlot(points: numpy.ndarray, figure: matplotlib.figure.Figure = None, **kwargs) -> None:
    """Plot points.

    Arguments:
    points -- points to be plotted, nx(>=2) numpy.ndarray
    **kwargs -- keyword arguments to be passed to plot
    """
    if figure is None:
        figure = pyplot.gcf()

    figure.axes[0].plot(points[:, 0], points[:, 1], **kwargs)


@plot_only
def groupsScatter(groups: numpy.ndarray, figure: matplotlib.figure.Figure = None, **kwargs) -> None:
    """Scatter points inside groups.

    Arguments:
    groups -- list of grouped points, m-list of x2 numpy.ndarrays
    **kwargs -- keyword arguments to be passed to scatter
    """

    for _g in groups:
        pointsScatter(_g, figure, **kwargs)


@plot_only
def groupsPlot(groups: numpy.ndarray, figure: matplotlib.figure.Figure = None, **kwargs) -> None:
    """Plot points inside groups.

    Arguments:
    groups -- list of grouped points, m-list of x2 numpy.ndarrays
    **kwargs -- keyword arguments to be passed to plot
    """

    for _g in groups:
        pointsPlot(_g, figure, **kwargs)


@plot_only
def grouplayersScatter(grouplayers: numpy.ndarray, figure: matplotlib.figure.Figure = None, **kwargs) -> None:
    """Scatter points from layers of all groups.

    Arguments:
    grouplayers -- points in all layers, n-list of (layer_count)-lists of x2 numpy.ndarray
    **kwargs -- keyword arguments to be passed to scatter
    """

    for _g in grouplayers:
        groupsScatter(_g, figure, **kwargs)


@plot_only
def grouplayersPlot(grouplayers: numpy.ndarray, figure: matplotlib.figure.Figure = None, **kwargs) -> None:
    """Plot points from layers of all groups.

    Arguments:
    grouplayers -- points in all layers, n-list of (layer_count)-lists of x2 numpy.ndarray
    **kwargs -- keyword arguments to be passed to plot
    """

    for _g in grouplayers:
        groupsPlot(_g, figure, **kwargs)
