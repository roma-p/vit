import os
import json

from vit import constants
from vit import py_helpers

def create_vite_fil_config(
        path, 
        repository_format_version=0,
        origin=True,
        origin_url=None,
        remote=False
        ): 
    py_helpers.write_json(
        os.path.join(path, constants.VIT_DIR, constants.VIT_CONFIG),
        {
            "core": {
                "repository_format_version": repository_format_version,
            },
            "repository": {
                "origin_url": _generate_origin_url(path),
            }, 
            "current_copy": {
                "is_origin": origin, 
                "is_working_copy_remote": remote
            }
        }
    )

def _generate_origin_url(path): 
    return os.path.join(py_helpers.get_hostname(), ":", path)