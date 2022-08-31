import os
import uuid
from vit import constants
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_package import TreePackage
from vit.custom_exceptions import *

def get_vit_repo_config_path(path, file_id):
    return os.path.join(path, constants.VIT_DIR, file_id)

def get_dot_vit_file(path, file_path):
    return os.path.join(path, constants.VIT_DIR, file_path)

# MISC ------------------------------------------------------------------------

def localize_path(local_path, raw_path):
    return os.path.join(local_path, raw_path)

# TEMPLATE --------------------------------------------------------------------

def get_index_template_path(local_repo_path):
    return get_dot_vit_file(local_repo_path, constants.VIT_TEMPLATE_CONFIG)

def get_template_path(local_repo_path, template_file_name):
    return os.path.join(
        constants.VIT_DIR,
        constants.VIT_TEMPLATE_DIR,
        template_file_name
    )

# ASSET -----------------------------------------------------------------------

def get_asset_file_path_raw(package_path, asset_name):
    return os.path.join(package_path, asset_name)

def generate_unique_asset_file_name(asset_name, extension):
    return "{}-{}{}".format(asset_name, uuid.uuid4(), extension)

def generate_asset_file_name_local(asset_name, suffix, extension):
        return "{}-{}{}".format(asset_name, suffix, extension)

def generate_unique_asset_file_path(package_path, asset_name, extension):
    return os.path.join(
        package_path,
        asset_name,
        generate_unique_asset_file_name(asset_name, extension)
    )


def get_asset_file_tree(ssh_connection, path, package_path, asset_name):
    # refacto me.

    ssh_connection.get_vit_file(path, constants.VIT_PACKAGES)

    with IndexPackage(path) as package_index:
        package_file_name = package_index.get_package_tree_file_path(package_path)
    if not package_file_name:
        raise Package_AlreadyExists_E(package_path)

    ssh_connection.get(
        package_file_name,
        localize_path(path, package_file_name)
    )

    with TreePackage(os.path.join(path, package_file_name)) as tree_package:
        asset_file_tree_path = tree_package.get_asset_tree_file_path(asset_name)
    if not asset_file_tree_path:
        raise Asset_NotFound_E(package_path, asset_name)

    if not os.path.exists(localize_path(path, os.path.dirname(asset_file_tree_path))):
        os.makedirs(localize_path(path, os.path.dirname(asset_file_tree_path)))

    ssh_connection.get(
        asset_file_tree_path,
        os.path.join(path, asset_file_tree_path)
    )
    return asset_file_tree_path