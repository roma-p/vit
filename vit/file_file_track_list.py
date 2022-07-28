import os
import json

from vit import constants
from vit import py_helpers
from vit import path_helpers

cfg_filepath = constants.VIT_TRACK_FILE

def create(path):
    return py_helpers.create_empty_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
    )

def add_tracked_file(path, filepath, force=False):
    if force: 
        sha = "0"
    else: 
        sha = py_helpers.calculate_file_sha(
            os.path.join(
                path,
                filepath
            )
        )
    return py_helpers.update_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
        {
            filepath: sha
        }
    )

def list_changed_files(path):
    ret = []
    json_data = py_helpers.parse_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath)
    )
    for file_path, stored_sha in json_data.items():
        print(file_path)
        current_sha = py_helpers.calculate_file_sha(
            os.path.join(
                path, 
                file_path
            )
        )

        if stored_sha != current_sha:
            ret.append(file_path)
    return tuple(ret)

def clean(path): 
    return py_helpers.update_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
        {}
    )
