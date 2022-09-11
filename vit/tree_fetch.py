from vit import constants
from vit import path_helpers
from vit.custom_exceptions import *
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_asset import TreeAsset
from vit.file_handlers.tree_package import TreePackage


def get_tree_package_path_from_package_name(local_path, package_path):
    with IndexPackage(local_path) as package_index:
        package_file_name = package_index.get_package_tree_file_path(package_path)
    if not package_file_name:
        raise Package_NotFound_E(package_path)
    return package_file_name


def get_tree_asset_path_from_package_tree_path_and_asset_name(
        local_path,
        tree_package_path,
        package_path,
        asset_name):
    tree_package_path_local = path_helpers.localize_path(
        local_path,
        tree_package_path
    )
    with TreePackage(tree_package_path_local) as tree_package:
        asset_file_tree_path = tree_package.get_asset_tree_file_path(asset_name)
    if not asset_file_tree_path:
        raise Asset_NotFound_E(package_path, asset_name)
    return asset_file_tree_path

def fetch_tree_asset_path_from_package_and_asset_name(
        ssh_connection, local_path,
        package_path, asset_name):
    ssh_connection.get_vit_file(local_path, constants.VIT_PACKAGES)
    tree_package_path = get_tree_package_path_from_package_name(
        local_path,
        package_path
    )
    ssh_connection.get_auto(tree_package_path, tree_package_path, recursive=True)
    tree_asset_path = get_tree_asset_path_from_package_tree_path_and_asset_name(
        local_path, tree_package_path,
        package_path, asset_name
    )
    ssh_connection.get_auto(tree_asset_path, tree_asset_path, recursive=True)
    return tree_asset_path

def fetch_up_to_date_tree_asset(
        ssh_connection, local_path,
        package_path, asset_name):
    tree_asset_path = fetch_tree_asset_path_from_package_and_asset_name(
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
    tree_package_path = get_tree_package_path_from_package_name(
        local_path,
        package_path
    )
    ssh_connection.get_auto(tree_package_path, tree_package_path)
    tree_package_path_local = path_helpers.localize_path(
        local_path,
        tree_package_path
    )
    return TreePackage(tree_package_path_local), tree_package_path

