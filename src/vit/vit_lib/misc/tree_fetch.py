from vit import constants
from vit import path_helpers
from vit.vit_lib.misc import tree_func
from vit.custom_exceptions import *
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_asset import TreeAsset
from vit.file_handlers.tree_package import TreePackage


def fetch_up_to_date_tree_asset(
        ssh_connection, local_path,
        package_path, asset_name):
    tree_asset_path = _fetch_tree_asset_path_from_package_and_asset_name(
        ssh_connection, local_path,
        package_path, asset_name
    )
    tree_asset_path_local = path_helpers.localize_path(
        local_path,
        tree_asset_path
    )
    return TreeAsset(tree_asset_path_local), tree_asset_path


def fetch_up_to_date_tree_package(ssh_connection, local_path, package_path):
    ssh_connection.get_vit_file(local_path, constants.VIT_PACKAGES)
    tree_package_path = tree_func.get_tree_package_path_from_package_name(
        local_path,
        package_path
    )
    ssh_connection.get_auto(tree_package_path, tree_package_path)
    tree_package_path_local = path_helpers.localize_path(
        local_path,
        tree_package_path
    )
    return TreePackage(tree_package_path_local), tree_package_path


def _fetch_tree_asset_path_from_package_and_asset_name(
        ssh_connection, local_path,
        package_path, asset_name):
    ssh_connection.get_vit_file(local_path, constants.VIT_PACKAGES)
    tree_package_path = tree_func.get_tree_package_path_from_package_name(
        local_path,
        package_path
    )
    ssh_connection.get_auto(tree_package_path, tree_package_path, recursive=True)
    tree_asset_path = tree_func.get_tree_asset_path_from_package_tree_path_and_asset_name(
        local_path, tree_package_path,
        package_path, asset_name
    )
    ssh_connection.get_auto(tree_asset_path, tree_asset_path, recursive=True)
    return tree_asset_path
