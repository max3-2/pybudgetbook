"""Test plot ideas"""
import pandas as pd
import matplotlib.pyplot as plt
from pybudgetbook import bb_io

data = bb_io.load_concatenad_data()


# %% Grouping, plotting
dm = data.loc[data['Vendor'] == 'DM Drogerie']
dm_price_cat = dm.groupby('Group')['Price'].sum()
dm_discount = -dm_price_cat.pop('none')


fig, ax = plt.subplots()

_ = plt.pie(
    dm_price_cat, labels=dm_price_cat.index,
    autopct=lambda p: '{:.0f}%'.format(p * dm_price_cat.sum() / 100),
    startangle=90)

ax.set_title("DM Einkäufe nach Kategorie")

ax.annotate(f'Total: {dm_price_cat.sum():.2f} €',
            (0.15, 0.1), xycoords='subfigure fraction', horizontalalignment='left')
ax.annotate(
    f'Discount: {dm_discount:.2f} € ({dm_discount * 100/ dm_price_cat.sum():.1f} %)',
    (0.15, 0.06), xycoords='subfigure fraction', horizontalalignment='left')
