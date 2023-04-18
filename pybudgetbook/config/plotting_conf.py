"""Updates package wide plot settings"""
import matplotlib as mpl
from matplotlib.patches import Rectangle

mpl.rcParams.update({
    'figure.constrained_layout.use': True,

    'axes.grid': True,

    'grid.linewidth': 0.7,
    'grid.color': '#8C8080',

    'image.cmap': 'gray',
    'image.interpolation': 'none',
})


def default_rect(group, ax):
    text_rec = Rectangle((group['left'], group['top']), group['width'], group['height'],
                         ec='green', fc='none', lw=0.3)

    ax.add_patch(text_rec)
