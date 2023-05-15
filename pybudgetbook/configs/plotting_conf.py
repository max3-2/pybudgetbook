"""Updates package wide plot settings"""
import matplotlib as mpl
from matplotlib.patches import Rectangle


_def_style = {
    'figure.constrained_layout.use': True,

    'axes.grid': True,

    'grid.linewidth': 0.7,
    'grid.color': '#8C8080',

    'image.cmap': 'gray',
    'image.interpolation': 'none',
}


def default_rect(group, ax):
    """
    Creates a rectangle with default style from a group `Series` that holds
    the geometric parameters.

    Parameters
    ----------
    group : `pd.Series`
        Rectangle parameters
    ax : `mpl.axis`
        Target axis to plot the rectangle to
    """
    text_rec = Rectangle((group['left'], group['top']), group['width'], group['height'],
                         ec='green', fc='none', lw=0.6)

    ax.add_patch(text_rec)


def set_style():
    """Sets a default style for good receipt plotting."""
    mpl.rcParams.update(_def_style)
