"""
Package-wide config options which are synced with the config file on start.

move_on_parse: `bool`, defaults to `True`
    Move images to datafolder on parse. If false, images are copied.
data_folder: `Path`, defaults to None
    Folder with data of the parsed and loaded receipts, incl. archive data.
lang: `str`, defaults to `deu`
    Main language for pattern matching and tesseract, can be changed on the
    fly, this is just the preset.
receipt_aliases: `dict`
    Coontains aliases of strngs found in the specific receipts to identify
    the vendor.
receipt_types: `dict`
    Maps vendors found by aliases or vendor.lower() pattern matching to a
    receipt type. This type then determines the pattern used for matching.
    Patterns are defined in constants, only change if you know what you are
    doing!
_negative_groups: `dict`
    MHolds lang. spec. lists of small words and patterns to trash when adding
    new items to groups, so some of the clustering is prevented.
"""
move_on_parse = True
data_folder = None
lang = 'deu'

# Search aliases for receipts
receipt_aliases = {
    'DM Drogerie': ['DM-Drogerie', 'dm.de', 'dm-'],
    'Edeka': ['lieben[ _]lebensmittel'],
}

# Maps receipt types to pattern types
receipt_types = {
    'Aldi': 'gen',
    'Edeka': 'gen',
    'Nahkauf': 'gen',
    'DM Drogerie': 'dm',
    'Unverpackt': 'unverpackt',
}

_negative_groups = {'deu': ['stück', 'stk', 'gourmet', 'premium', 'prem'],
                    'eng': [],
                    'fra': [],
                    }
