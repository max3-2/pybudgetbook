"""pybudgetbook main init"""
__version__ = '0.1.0'
__name__ = 'pybudgetbook'


from pybudgetbook.config.config_tools import _check_config, load_config

# On init, check config
_check_config()
load_config()

# TODO UI
# Add field for rabatt
# TODO live language setting from combo and not from options, search options['lang]
# add rotate mode,  output field, delay to update, auto rotate funcs

# cid = fig.canvas.mpl_connect(
#     'key_press_event', lambda event: rot_event(ax[1], event))
# TODO Rotation is the most important factor to get a good ocr! Build a UI
# tool with a small delay before re-filtering
# def rot_event(act_ax, event):
#     if event.inaxes is act_ax:
#         if event.key == 'right':
#             print('rot right')
#         elif event.key == 'left':
#             print('rot left')
#         elif event.key == 'shift+right':
#             print('rot right much')
#         elif event.key == 'shift+left':
#             print('rot left much')
#         else:
#             return
