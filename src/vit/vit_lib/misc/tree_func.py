from vit.custom_exceptions import *
from vit import path_helpers
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_package import TreePackage
from vit.file_handlers.tree_asset import TreeAsset


def become_editor_of_asset(tree_asset, asset_name, asset_filepath, user):
    editor = tree_asset.get_editor(asset_filepath)
    if editor and editor != user:
        raise Asset_AlreadyEdited_E(asset_name, editor)
    tree_asset.set_editor(asset_filepath, user)


def get_local_tree_package(local_path, package_path):
    path = get_tree_package_path_from_package_name(
        local_path,
        package_path
    )
    path = path_helpers.localize_path(local_path, path)
    return TreePackage(path), path


def get_local_tree_asset(local_path, package_path, asset_name):
    tree_package_path = get_tree_package_path_from_package_name(
        local_path,
        package_path
    )
    path = get_tree_asset_path_from_package_tree_path_and_asset_name(
        local_path,
        tree_package_path,
        package_path,
        asset_name
    )
    path = path_helpers.localize_path(local_path, path)
    return TreeAsset(path), path


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
