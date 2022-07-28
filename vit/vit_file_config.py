import os
import json

from vit import constants
from vit import py_helpers

def vit_file_package_create(path):
    return py_helpers.create_empty_json(
        _get_vit_file_config_path(path, constants.VIT_packageS),
    )

def vit_file_package_reference_new_package(path, uid, package_path):
    return py_helpers.update_json(
        _get_vit_file_config_path(path, constants.VIT_packageS),
        {uid:package_path}
    )

def _get_vit_file_config_path(path, file_id): 
    return os.path.join(path, constants.VIT_DIR, file_id)

def _generate_origin_url(path): 
    return os.path.join(py_helpers.get_hostname(), ":", path)
