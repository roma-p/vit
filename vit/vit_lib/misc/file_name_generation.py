from vit import py_helpers
from vit import constants
import uuid
import os


def generate_unique_asset_file_name(asset_name, extension):
    return "{}-{}{}".format(asset_name, uuid.uuid4(), extension)


def generate_checkout_file_name(asset_name, suffix, extension):
    return "{}-{}{}".format(asset_name, suffix, extension)


def generate_checkout_path(
        origin_file_path, package_path,
        asset_name, suffix):
    extension = py_helpers.get_file_extension(origin_file_path)
    asset_name_local = generate_checkout_file_name(
        asset_name,
        suffix,
        extension
    )
    asset_path = os.path.join(package_path, asset_name_local)
    return asset_path


def generate_unique_asset_file_path(package_path, asset_name, extension):
    return os.path.join(
        package_path,
        asset_name,
        generate_unique_asset_file_name(asset_name, extension)
    )


def generate_asset_tree_file_path(package_path, asset_name):
    return os.path.join(
        constants.VIT_DIR,
        constants.VIT_ASSET_TREE_DIR,
        generate_package_tree_dir_name(package_path),
        "{}.json".format(asset_name)
    )


def generate_package_tree_file_path(package_path):
    return os.path.join(
        constants.VIT_DIR,
        constants.VIT_ASSET_TREE_DIR,
        generate_package_tree_file_name(package_path),
    )


def generate_package_tree_dir_name(package_path):
    return package_path.replace("/", "-")


def generate_package_tree_file_name(package_path):
    return package_path.replace("/", "-")+".json"
