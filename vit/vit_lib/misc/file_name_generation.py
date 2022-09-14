from vit import py_helpers
from vit import constants
import uuid
import os
import re

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


def generate_package_tree_dir_name(package_path):
    return package_path.replace("/", "-")


def generate_package_tree_file_name(package_path):
    return package_path.replace("/", "-")+".json"


def generate_tag_auto_name_prefix(asset, branch):
    return "{}-{}-v".format(asset, branch)


def generate_tag_auto_regexp(asset, branch):
    return "{}[0-9].[0-9].[0-9]".format(
        generate_tag_auto_name_prefix(asset, branch)
    )


def generate_tag_auto_name_by_branch(asset, branch, major, minor, patch):
    return "{}{}.{}.{}".format(
        generate_tag_auto_name_prefix(asset, branch),
        major, minor, patch
    )


def get_version_from_tag_auto(tag_name):
    ret = re.findall("[0-9]", tag_name)
    return tuple([int(i) for i in ret])


def check_is_auto_tag(asset, branch, tag_name):
    regxp = generate_tag_auto_regexp(asset, branch)
    return bool(re.match(regxp, tag_name))


def increment_version(index_to_increment, *version_numbers):
    version_numbers = list(version_numbers)
    version_numbers[index_to_increment] += 1
    for i in range(index_to_increment + 1, len(version_numbers)):
        version_numbers[i] = 0
    return tuple(version_numbers)
