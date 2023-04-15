"""
Package-wide config options which are synced with the config file on start.

move_on_parse: `bool`, defaults to `True`
    Move images to datafolder on parse. If false, images are copied.
data_folder: `Path`, defaults to None
    Folder with data of the parsed and loaded receipts, incl. archive data.
lang: `str`, defaults to `deu`
    Main language for pattern matching and tesseract, can be changed on the
    fly, this is just the preset.
"""
move_on_parse = True
data_folder = None
lang = 'deu'
