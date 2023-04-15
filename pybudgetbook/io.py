"""Manages folder structure of data folder and IO of data"""
from pathlib import Path

# Move to constants
_FOLDER_STRUCT = {'data': {'receipts': None,
                           'images': None},
                  'backup': None,
                  'export': None,
                  }


def make_folder_structure(root, template):
    def one_directory(dic, path):
        for name, info in dic.items():
            next_path = path / Path(name)
            next_path.mkdir(parents=True, exist_ok=True)
            if isinstance(info, dict):
                one_directory(info, next_path)

    one_directory(template, Path(root))

    print('Done, ok!')


def _concatenate_to_main(dataframe, work_dir):
    ...


def save_with_metadata(dataframe):
    # TODO ideas are tags,
    ...


def load_with_metadata(dataframe):
    ...
