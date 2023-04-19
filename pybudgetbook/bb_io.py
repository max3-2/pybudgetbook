"""Manages folder structure of data folder and IO of data"""
from pathlib import Path

# TODO MAKE RELATIVE
import pybudgetbook.config.constants as bbconstant
import pybudgetbook.config.config as bbconfig


def load_group_match_data(lang):
    # TODO change path to module.__file__
    basic_data = 1
    user_data = 1

    # combine dicts use all values - those are lists. better make this
    # manual
    # a = {1:["A"]}
    # b = {1:["b"], 2:["C"]}

def _concatenate_to_main(dataframe, work_dir):
    ...


def save_with_metadata(dataframe):
    # TODO ideas are tags,
    ...


def load_with_metadata(dataframe):
    ...
