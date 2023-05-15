"""
Package-wide config options which are synced with the config file on start.
To have a good sync, the ones accessed by the file are kept in a dict. The ones
which are not in a dict are not supposed to be edited!

data_folder: `Path`, defaults to None
    Folder with data of the parsed and loaded receipts, incl. archive data.

move_on_parse: `bool`, defaults to `True`
    Move images to datafolder on parse. If false, images are copied.

lang: `str`, defaults to `deu`
    Main language for pattern matching and tesseract, can be changed on the
    fly, this is just the preset.

generate_unique_name

show_logger_on_start

logger_popup_level

logger_show_debug

ask_for_image


The following values should only be edited if you know what you are doing

receipt_aliases: `dict`
    Coontains aliases of strngs found in the specific receipts to identify
    the vendor.

receipt_types: `dict`
    Maps vendors found by aliases or vendor.lower() pattern matching to a
    receipt type. This type then determines the pattern used for matching.
    Patterns are defined in constants, only change if you know what you are
    doing!

needs_tax_switch: `dict`

"""
# TODO update docu values
options = {
    'data_folder': None,
    'move_on_save': True,
    'lang': 'deu',
    'generate_unique_name': True,
    'show_logger_on_start': False,
    'logger_popup_level': 20,
    'logger_show_debug': False,
    'ask_for_image': True,
}

# Search aliases for receipts
receipt_aliases = {
    'DM Drogerie': ['DM-Drogerie', 'dm.de', 'dm-'],
    'Edeka': ['lieben[ _]lebensmittel'],
    'Tankstelle': ['aral', 'shell', 'jet', 'eni', 'tank', 'tankstelle'],
    'Aldi': ['aldi', 'aldl', 'aidi'],
    'Real': ['real', 'rael'],
    'Raiffeisen': ['zg', 'raiff'],
    'Rewe': ['rewe', 'rwe', 'r_e_w_e']
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
    'General': 'gen',
}

# Maps from -> to if tax switching is needed for a vendor.
needs_tax_switch = {
    'Aldi': (1, 2),
}
