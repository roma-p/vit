import os
import json

from vit import constants
from vit import py_helpers
from vit import path_helpers

cfg_filepath = constants.VIT_CONFIG

def create(
        path, 
        repository_format_version=0,
        origin=True,
        origin_url=None,
        remote=False):
    py_helpers.write_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath),
        {
            "core": {
                "repository_format_version": repository_format_version,
            },
            "origin_config": {
            }, 
            "current_copy": {
                "is_origin": origin, 
                "is_working_copy_remote": remote
            },
            "origin_link": {
                "host": None, 
                "path": None,
                "username": None,
            }
        }
    )

def edit_on_clone(path, origin_host, origin_path, username): 
    py_helpers.update_json(
        path_helpers.get_vit_file_config_path(path, cfg_filepath), 
        {
            "origin_config": {
            },
            "current_copy": {
                "is_origin": False
            }, 
            "origin_link": {
                "host": origin_host, 
                "path": origin_path, 
                "username": username
            }
        }
    )

def get_origin_ssh_info(path): 
    data = py_helpers.get_json_main_key(
        path_helpers.get_vit_file_config_path(path, cfg_filepath), 
        "origin_link"
    )
    return data["host"], data["path"], data["username"] 
