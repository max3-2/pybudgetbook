"""
Package-wide config options and parsers

move_on_parse: `bool`, defaults to `True`
    Move images to datafolder on parse. If false, images are copied.
data_folder: `Path`, defaults to None
    Folder with data of the parsed and loaded receipts, incl. archive data.
"""
move_on_parse = True
data_folder = None
