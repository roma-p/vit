import os
import json
from collections import defaultdict

from vit import constants
from vit import py_helpers
from vit import path_helpers

cfg_filepath = constants.VIT_TRACK_FILE

def create(path):
    return py_helpers.create_empty_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
    )

def add_tracked_file(
        path, package_path, asset_name,
        filepath, branch, force=False):
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
            filepath: [sha, package_path, asset_name, branch]
        }
    )

def get_files_data(path):
    ret = []
    json_data = py_helpers.parse_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath)
    )
    for file_path, data_in in json_data.items():
        current_sha, package_path, asset_name, branch = data_in
        data_out = (
            file_path,
            package_path,
            asset_name,
            branch,
            not _is_same_sha(
                os.path.join(path, file_path),
                current_sha
            )
        )
        ret.append(data_out)
    return tuple(ret)

def gen_status_local_data(path):
    nested_dict = lambda: defaultdict(nested_dict)
    ret = nested_dict()

    json_data = py_helpers.parse_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath)
    )
    for file_path, (stored_sha, package_path, asset_name, branch) in json_data.items():
        modification_to_commit = not _is_same_sha(
            os.path.join(path, file_path),
            stored_sha
        )
        ret[package_path][asset_name][branch] = {
            "file": file_path,
            "to_commit": modification_to_commit
        }
    return ret

def clean(path):
    return py_helpers.override_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
        {}
    )

def remove_file(path, file_path):
    json_data = py_helpers.parse_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath)
    )
    if file_path not in json_data:
        return
    json_data.pop(file_path, None)
    py_helpers.override_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
        json_data
    )
def _is_same_sha(file_complete_path, current_sha):
    return current_sha == py_helpers.calculate_file_sha(file_complete_path)
