"""Updates package wide plot settings"""
import matplotlib as mpl
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_def_style = {
    'figure.constrained_layout.use': True,

    'axes.grid': False,

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


def create_stem(data, ax):
    """
    Creates a per vendor stem plot and a cumsum on the other axis. Offsetting
    the stem is quite complex but working like this. TLDR: Plots are created by
    vendor and depending on the amount of stems at a location and the current
    plot index and the amount of stems actually plotted at a location the
    offset is computed in time domain.

    Parameters
    ----------
    data : `pd.DataFrame`
        Input data, if needed time filter before!
    ax : `mpl.axes`
        Axes to create the plot on
    """
    # Group and bin
    grouped = data.groupby([pd.Grouper(
        key='Date', freq='W', closed='left', label='left'),
        'Vendor'])['Price'].sum().reset_index()
    grouped['Date'] += pd.to_timedelta('4d')

    # Get the 5 main with colors, the rest is gray
    top_five = grouped.groupby(
        'Vendor')['Price'].sum().sort_values(ascending=False)[:5].index
    colors = {name: color for name, color
              in zip(top_five, plt.rcParams['axes.prop_cycle'].by_key()['color'])}

    locations = grouped['Vendor'].unique()

    # Create an offset for x-axis positions and use them
    offset = np.ptp(grouped['Date']) / 100  # Offset of 6 hours for day-level resolution

    location_count = grouped.groupby('Date')['Vendor'].nunique()
    used_offsets = location_count.copy()
    used_offsets[:] = 0

    # Plotting
    ax2 = ax.twinx()
    ax2.plot(grouped['Date'], grouped['Price'].cumsum(), ls='--')

    for i, loc in enumerate(locations):
        loc_data = grouped[grouped['Vendor'] == loc]
        count_per_loc = location_count[loc_data['Date']].values
        offset_here = used_offsets[loc_data['Date']].values

        offset_per_loc = (offset_here - (count_per_loc - 1) / 2)
        offset_per_loc[count_per_loc == 1] = 0

        used_offsets[loc_data['Date']] += 1

        x = loc_data['Date'] + offset * offset_per_loc
        y = loc_data['Price']

        color = colors.get(loc, 'gray')
        if color == 'gray':
            loc = None
        # Plot the lines
        stems = ax.stem(x, y, linefmt=color, basefmt='none', markerfmt='o', label=loc)
        # Plot the markers as empty circles with different edge colors
        stems.markerline.set_markerfacecolor('none')
        stems.markerline.set_markersize(4)

    # Set the x-axis labels to be the months and format with WoY
    _ = ax.set_xticks(
        grouped['Date'].unique(),
        labels=grouped['Date'].unique().strftime('2023-%U'),
        rotation=35)

    ax2.set_ylim(0, None)

    # Add legend
    ax.legend(loc='best')

    # and labels
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount per Shop [€]')
    ax2.set_ylabel('Amount Total [€]')

    # and padding
    ax.figure.set_layout_engine('constrained')

