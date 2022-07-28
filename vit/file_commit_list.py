import os
import json

from vit import constants
from vit import py_helpers
from vit import path_helpers

cfg_filepath = constants.VIT_NON_COMMITTED_FILE

def create(path): 
    return py_helpers.create_empty_file(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
    )


def add_file(path, filepath):
    return py_helpers.append_line_to_file(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
        filepath
    )

def get_files(path):
    return py_helpers.read_lines_from_file(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
    )


def clean(path):
    return py_helpers.erase_file_content(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
    )
