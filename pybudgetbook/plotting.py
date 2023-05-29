"""Updates package wide plot settings"""
import logging
import matplotlib as mpl
from matplotlib.patches import Rectangle, Shadow
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from darkdetect import isDark

from .configs.config import options


logger = logging.getLogger(__package__)


_def_style = {
    'figure.constrained_layout.use': True,

    'axes.grid': False,

    'grid.linewidth': 0.7,
    'grid.color': '#8C8080',

    'image.cmap': 'gray',
    'image.interpolation': 'none',
}


def _dbl_fmt(val, sum_vals, label_cutoff):
    """Shows a number in float format and percent"""
    rel_val = val * 100 / sum_vals
    return f'{val:.2f} {options["currency"]:s} ({rel_val:.2f}%)' if rel_val >= label_cutoff else ''


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

    if isDark():
        logger.debug('Dark mode plotting style')
        dark_update = {
            'figure.facecolor': '#404040',
            'axes.facecolor': '#404040',

            'text.color': '#f0f0f0',
            'axes.titlecolor': '#f0f0f0',
            'axes.edgecolor': '#f0f0f0',
            'axes.labelcolor': '#f0f0f0',
            'xtick.color': '#f0f0f0',
            'xtick.labelcolor': '#f0f0f0',
            'ytick.color': '#f0f0f0',
            'ytick.labelcolor': '#f0f0f0',
            'legend.edgecolor': '#f0f0f0',

            'grid.color': '#565055',
        }
        mpl.rcParams.update(dark_update)

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
    # Get oldest, time span and compute max ticks
    date_span = (data['Date'].max() - data['Date'].min()).days
    reduce_by = int(round((date_span / 7) // 18))
    grouper_freq = f'{reduce_by + 1:d}W'

    # Group and bin
    grouped = data.groupby([pd.Grouper(
        key='Date', freq=grouper_freq, closed='left', label='left'),
        'Vendor'])['Price'].sum().reset_index()
    grouped['Date'] += pd.to_timedelta('4d')

    # Get the 4 main with colors, the rest is gray and gets summed up
    by_price = grouped.groupby(
        'Vendor')['Price'].sum().sort_values(ascending=False)
    top_four = by_price[:4]
    rest_of_the_crew = by_price[4:].index.unique()
    grouped.loc[grouped['Vendor'].isin(rest_of_the_crew), 'Vendor'] = "Smaller"

    colors = {name: color for name, color
              in zip(top_four.index, plt.rcParams['axes.prop_cycle'].by_key()['color'])}

    locations = grouped['Vendor'].unique()

    # Create an offset for x-axis positions and use them
    offset = np.ptp(grouped['Date']) / 100  # Offset of 6 hours for day-level resolution

    location_count = grouped.groupby('Date')['Vendor'].nunique()
    used_offsets = location_count.copy()
    used_offsets[:] = 0

    # Plotting
    ax2 = ax.twinx()
    ax2.plot(grouped['Date'], grouped['Price'].cumsum(), ls='--')

    sorting = grouped.groupby('Vendor')['Price'].sum().sort_values(ascending=False)
    for loc in sorting.index:
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
            label = None
        else:
            label = loc + f': {top_four[loc]:.2f} {options["currency"]}'

        # Plot the lines
        stems = ax.stem(x, y, linefmt=color, basefmt='none', markerfmt='o', label=label)
        # Plot the markers as empty circles with different edge colors
        stems.markerline.set_markerfacecolor('none')
        stems.markerline.set_markersize(4)

    # Set the x-axis labels to be the months and format with WoY
    _ = ax.set_xticks(
        grouped['Date'].unique(),
        labels=grouped['Date'].unique().strftime('2023-%U'),
        rotation=35)

    # Compute hline per tick
    hline_range = (used_offsets * offset / 2)
    hline_start = used_offsets.index

    basecolor = 'white' if isDark() else 'black'
    for hline, hline_r in zip(hline_start, hline_range):
        line = ax.plot((hline-hline_r, hline+hline_r), (0, 0), ls='--',
                       color=basecolor, marker='|', markersize=6)

    ax2.set_ylim(0, None)

    # Add legend
    ax.legend(loc='best', title='Top 5')

    # and labels
    ax.set_xlabel('Date')
    ax.set_ylabel(f'Amount per Shop [{options["currency"]}]')
    ax2.set_ylabel(f'Amount Total [{options["currency"]}]')

    # and padding
    ax.figure.set_layout_engine('constrained')


def bar_fmt(values, fmt_type, label_cutoff):
    """
    Formats values to bar labels as used in the `matplotlib` `bar_label`
    function. This is just a simple warpper around some more useful cases for
    number display.

    Currently, possible options are specified using a `str` which can be one of
    `off`, `abs`, `rel`, `both`.
    """
    values = np.array(values).astype(float)
    total = np.nansum(values)
    if fmt_type == 'off':
        return values, ''

    elif fmt_type == 'abs':
        return (
            values,
            lambda val: f'{val:.2f} {options["currency"]:s}' if val * 100 / total >= label_cutoff else ''
        )

    elif fmt_type == 'rel':
        values = values * 100 / total
        return values, lambda val: f'{val:.2f} %' if val * 100 / total >= label_cutoff else ''

    elif fmt_type == 'both':
        return values, lambda val: _dbl_fmt(val, np.nansum(values), label_cutoff)

    else:
        raise IOError('Invalid bar label format')


class PieEventHandler:
    """
    This class handles the display of a pie plot with some configurable
    display options. If clicked on a sample of the pie, the sample is
    highlighted and a bar plot can be used to show details. This is best
    used with a dataframe and different grouping calls.

    Example usage:
    ```
    data = np.array([24, 15, 10, 32, 7])
    labels = ['Dogs', 'Logs', 'Hogs', 'Rocks', 'n.a.']

    details = {'Rocks': ([14, 8, 5, 5], ['Emerald', 'Saphire', 'Gold', 'Silver']),
            'Logs': ([8, 4, 3], ['Oak', 'Maple', 'Beech'])}

    fig, (ax_p, ax_b) = plt.subplots(1, 2)

    pieplot = ax_p.pie(data, labels=labels, autopct='%.1f')
    ph = PieEventHandler(pieplot, details, ax_b, bar_labels='both')
    ```
    """
    def __init__(self, pieplot, bar_details={}, bar_axes=None,
                 click_explode=0.2, click_ew=1.3, bar_labels='abs',
                 reduce_df=None, label_cutoff=0.):
        """
        Creates the handler on the pieplot and attaches a bar plot for details
        if the needed inputs are provided. See below for an explanation of
        the correct inputs.

        Parameters
        ----------
        pieplot : `mpl.pie`
            Instance of a pieplot that has been drawn to a given axes. This
            will be used for handling the other functions. Mind the correct
            labeling if you want to use bars, see next
        bar_details : `dict`, `pd.DataFrame`, optional
            This provides the details the bar should how. It must have the
            same keys as the labels from the pie plots, since they will be used
            for loookup. This can be anything with a `.get()` method defined,
            most likely a `dict` or a `DataFrame`, by default {}
        bar_axes : `mpl.axes`, optional
            Axes on which the bar plot should be drawn, by default None
        click_explode : `float`, optional
            The amount of explosion applied to an active pie, by default 0.2
        click_ew : `float`, optional
            The edgewidth to highlight am active pie, by default 1.3
        `bar_labels` : `str`, optional
            Bar labels to generate on the bar plot. This uses the `bar_fmt`
            function, so see there for possible options, by default 'abs'
        `reduce_df` : `tuple`
            Optional tuple working with dataframe bar details input. First is
            a selection of a column to compare with the pie slice label,
            second is the following groupby to reduce data for plotting.
            Defaults to `None`
        `label_cutoff` : `float`, optional
            Cutoff label display if value is below a certain percent. Defaults
            to `0` which shows all labels
        """
        self.pieplot = pieplot
        self.bar_details = bar_details
        self.bar_ax = bar_axes
        self.fig = pieplot[0][0].figure
        self.ax = pieplot[0][0].axes

        self.click_explode = click_explode
        self.click_ew = click_ew

        assert bar_labels in ('off', 'abs', 'rel', 'both'), "Invalid bar label"
        self.bar_labels = bar_labels

        if self.bar_ax is not None:
            self.bar_ax.axis('off')
            self.fig.canvas.draw()

        self.cid = self.fig.canvas.mpl_connect('button_press_event',
                                               self.onclick)
        self._curr_bar_text = None
        self._ex_wedge_idx = None
        self._nom_label_pos = None
        self._nom_val_pos = None
        self._curr_shadow = None
        self.reduce_df = reduce_df
        self.label_cutoff = label_cutoff

    def cust_explode(self, index, expl):
        """Explodes a pie element from the rest of the plot."""
        wedge = self.pieplot[0][index]
        label = self.pieplot[1][index]

        # Move wedge
        x, y = wedge.center
        # theta2 = (wedge.theta1 + wedge_frac) if counterclock else (wedge.theta1 - wedge_frac)
        thetam = np.deg2rad(0.5 * (wedge.theta1 + wedge.theta2))  # 2 * np.pi *
        x += expl * np.cos(thetam)
        y += expl * np.sin(thetam)
        wedge.set_center((x, y))

        # Move label
        x, y = label.get_position()
        self._nom_label_pos = (x, y)
        x += expl * np.cos(thetam)
        y += expl * np.sin(thetam)
        label.set_position((x, y))
        label.set_fontweight('bold')

        # Move number if there
        if len(self.pieplot) == 3:
            number = self.pieplot[2][index]
            x, y = number.get_position()
            self._nom_val_pos = (x, y)
            x += expl * np.cos(thetam)
            y += expl * np.sin(thetam)
            number.set_position((x, y))
            number.set_fontweight('bold')

        # Add shadow
        if self._curr_shadow is not None:
            self._curr_shadow.remove()
        self._curr_shadow = Shadow(wedge, -0.02, -0.02, label='_nolegend_')
        self.ax.add_patch(self._curr_shadow)

    def reset_explode(self, index):
        """Resets an exploded pie to go back into the main chart."""
        wedge = self.pieplot[0][index]
        label = self.pieplot[1][index]

        wedge.set_center((0, 0))
        label.set_position(self._nom_label_pos)
        label.set_fontweight('normal')

        if len(self.pieplot) == 3:
            number = self.pieplot[2][index]
            number.set_position(self._nom_val_pos)
            number.set_fontweight('normal')

        # Remove shadow
        if self._curr_shadow is not None:
            self._curr_shadow.remove()
            self._curr_shadow = None

    def add_barplot(self, index):
        """Creates the bar plot with the details on the second axes."""
        self._curr_bar_text = None
        self.bar_ax.cla()
        self.bar_ax.axis('off')
        current_details = False

        if self.reduce_df is not None:
            if self.bar_details[self.reduce_df[0]].isin([(this_det := self.pieplot[1][index].get_text())]).any():
                current_data = self.bar_details[
                    self.bar_details[self.reduce_df[0]] == this_det].groupby(
                    self.reduce_df[1])['Price'].sum().abs()
                values = current_data.values
                barlabels = current_data.index
                current_details = True
        else:
            if (this_det := self.pieplot[1][index].get_text()) in self.bar_details:
                values, barlabels = self.bar_details[this_det]
                current_details = True

        if current_details:
            bottom = 1
            width = 0.5
            color = self.pieplot[0][index].get_facecolor()[0:3]

            shades = np.linspace(0.3, 1, len(values))

            values, fmt = bar_fmt(values, self.bar_labels, self.label_cutoff)
            sort_vals = np.argsort(values)

            # Sort and blank
            values = values[sort_vals]
            barlabels = np.array(barlabels)[sort_vals]

            for height, label, shade in zip(values[::-1], barlabels[::-1], shades[::-1]):
                bottom -= height
                self._barplot = self.bar_ax.bar(
                    0, height, width, bottom=bottom, color=color, label=label,
                    alpha=shade)

                self.bar_ax.bar_label(
                    self._barplot, fmt=fmt, label_type='center')

            self.bar_ax.set_title(f'Details for {this_det:s}')
            self.bar_ax.legend(loc='upper right')
            self.bar_ax.set_xlim(- 1.5 * width, 1.5 * width)

        else:
            self.bar_ax.set_xlim(0, 1)
            self.bar_ax.set_ylim(0, 1)
            self._curr_bar_text = self.bar_ax.annotate(
                'No details available', (0.5, 0.5), fontweight='demi',
                verticalalignment='center', horizontalalignment='center')

    def onclick(self, event):
        """
        Main event handling the click and the generation of the additional
        plots and data.
        """
        if event.inaxes != self.ax:
            return

        click_id = np.argmax(
            [wedge.contains(event)[0] for wedge in self.pieplot[0]])

        # Reset all - this is not the best but helps with text reset
        for reset_index in range(len(self.pieplot[0])):
            self.pieplot[0][reset_index].set_linewidth(0)
            self.pieplot[0][reset_index].set_edgecolor('none')
            self.pieplot[0][reset_index].set_center((0, 0))
            if reset_index == self._ex_wedge_idx:
                self.reset_explode(reset_index)

        # Active clicked? Just reset...
        if self._ex_wedge_idx == click_id:
            self._ex_wedge_idx = None
            self._curr_bar_text = None
            self.bar_ax.cla()
            self.bar_ax.axis('off')
            self.fig.canvas.draw()
            return

        # Set current
        self.pieplot[0][click_id].set_linewidth(self.click_ew)
        self.pieplot[0][click_id].set_edgecolor('k')
        self.cust_explode(click_id, self.click_explode)
        self._ex_wedge_idx = click_id

        # Add details
        if self.bar_ax is not None:
            self.add_barplot(click_id)

        self.fig.canvas.draw()