"""
Package-wide config options which are synced with the config file on start.
To have a good sync, the ones accessed by the file are kept in a dict. The ones
which are not in a dict are not supposed to be edited!

data_folder: `Path`, defaults to None
    Folder with data of the parsed and loaded receipts, incl. archive data.
    Images are also stored here. Matching data is also stored here.

move_on_parse: `bool`, defaults to `True`
    Move images to datafolder on parse. If false, images are just copied.

lang: `str`, defaults to `deu`
    Main language for pattern matching and tesseract, can be changed on the
    fly, this is just the preset.

generate_unique_name: `bool`, defaults to `True`
    Generates unique save names if naming scheme would overwrite files.

show_logger_on_start: `bool`, defaults to `False`
    Show looging window on UI startup, this is usually not needed as a normal
    user.

logger_popup_level: `int`, defaults to `20`
    Logger level at which the logging window pops up. Default to `20` which is
    a warning. Can be lowered for debugging purposes.

logger_show_debug: `bool`, defaults to `False`
    Show the debug log outout, only used for debugging.

ask_for_image: `bool`, defaults to `True`
    If no image is connected to a current dataset, asks on save. Will not
    proceed if no image is added. Any image can be added. Image will be
    renamed an copied to the data folder (as with a receipt that relies on
    an image due to parsing).

The following values should only be edited if you know what you are doing

receipt_aliases: `dict`
    Contains aliases of `str` found in the specific receipts to identify
    the vendor.

receipt_types: `dict`
    Maps vendors found by aliases or vendor.lower() pattern matching to a
    receipt type. This type then determines the pattern used for matching.
    Patterns are defined in constants, only change them if you know what you
    are doing!

needs_tax_switch: `dict`
    Maps a vendor to a tuple defining a switch of tax classes. This is needed
    since there is not a consistent definition of numeric value / letter to a
    tax group and the final dataset should be consistent.
"""
options = {
    'data_folder': None,
    'move_on_save': True,
    'lang': 'deu',
    'generate_unique_name': True,
    'show_logger_on_start': False,
    'logger_popup_level': 20,
    'logger_show_debug': False,
    'ask_for_image': True,
    'currency': '€'
}

# Search aliases for receipts
receipt_aliases = {
    'DM Drogerie': ['DM-Drogerie', 'dm.de', 'dm-'],
    'Edeka': ['lieben[ _]lebensmittel'],
    'Tankstelle': ['aral', 'shell', 'jet', 'tank', 'tankstelle'],
    'Aldi': ['aldi', 'aldl', 'aidi'],
    'Real': ['real', 'rael'],
    'Raiffeisen': ['zg', 'raiff'],
    'ReweLieferung': ['lieferservice', 'lieferadresse', 'lieferung', 'rewe'],
    'Rewe': ['rewe', 'rwe', 'r_e_w_e'],
}

# Maps receipt types to pattern types
receipt_types = {
    'Aldi': 'gen',
    'Edeka': 'gen',
    'Nahkauf': 'gen',
    'DM Drogerie': 'dm',
    'Unverpackt': 'unverpackt',
    'Real': 'real',
    'Tankstelle': 'tank',
    'Raiffeisen': 'raiff',
    'Rewe': 'rewe',
    'ReweLieferung': 'rewe_delivery',
    'General': 'gen',
    'Simple': 'simple'
}

# Maps from -> to if tax switching is needed for a vendor.
needs_tax_switch = {
    'Aldi': (1, 2),
    'Edeka': (1, 2),
}
