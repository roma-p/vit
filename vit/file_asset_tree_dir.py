import os
import json

import logging
log = logging.getLogger()

import time
from vit import constants
from vit import py_helpers

DEFAULT_BRANCH = "base"

def create_asset_file_tree(path, package_path, asset_name, asset_filename, user):
    
    tree_file_path = get_asset_file_tree_path(
        path,
        package_path,
        asset_name)
    tree_dir_path = os.path.dirname(tree_file_path)

    file_path = os.path.join(
        package_path,
        asset_name,
        asset_filename
    )

    if not os.path.exists(tree_dir_path):
        os.makedirs(tree_dir_path)

    data = {
        "commits" : {},
        "branchs" : {}
    }
    data = add_commit(data, file_path, None, time.time(), user)
    data = set_branch(data, DEFAULT_BRANCH, file_path)
    py_helpers.write_json(tree_file_path, data)
    return tree_file_path

def add_commit(data, filepath, parent, date, user, ):
    data["commits"].update({
        filepath : {
            "parent": None,
            "date": date,
            "user": user, 
        }
    })
    return data

def set_branch(data, branch, filepath):
    data["branchs"][branch] = filepath
    return data

def get_asset_file_tree_path(path, package_path, asset_name):
    return os.path.join(
        path,
        constants.VIT_DIR,
        constants.VIT_ASSET_TREE_DIR, 
        _gen_package_dir_name(package_path),
        "{}.json".format(asset_name)
    )

def get_package_file_tree_path(path, package_path):
    return os.path.join(
        path,
        constants.VIT_DIR,
        constants.VIT_ASSET_TREE_DIR,
        _gen_package_dir_name(package_path)
    )

def get_branch_current_file(path, package_path, asset_name, branch):
    file_path = get_asset_file_tree_path(
        path,
        package_path,
        asset_name
    )
    data = py_helpers.parse_json(file_path)
    branch_ref = data["branchs"].get(branch, None)
    if not branch_ref:
        log.error("branch '{}' not found for {} {}".format(
            branch, package_path, asset_name
        ))
    return branch_ref       

def _gen_package_dir_name(package_path):
    return package_path.replace("/", "-")
