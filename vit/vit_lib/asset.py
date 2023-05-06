import os
import time

from vit import constants
from vit import path_helpers
from vit import py_helpers
from vit.vit_lib.misc import (
    tree_func,
    tree_fetch,
    file_name_generation
)
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.file_handlers.index_template import IndexTemplate
from vit.file_handlers.tree_asset import TreeAsset


def create_asset_from_file(
        vit_connection, package_path,
        asset_name, file_path):

    if not os.path.exists(file_path) or os.path.isdir(file_path):
        raise Path_FileNotFound_E(file_path)
    sha256 = py_helpers.calculate_file_sha(file_path)
    extension = py_helpers.get_file_extension(file_path)

    asset_file_path = _register_new_asset(
        vit_connection, package_path,
        asset_name, sha256, extension
    )

    vit_connection.create_dir_if_not_exists(os.path.dirname(asset_file_path))
    vit_connection.put(file_path, asset_file_path)


def create_asset_from_template(
        vit_connection, package_path,
        asset_name, template_id):

    template_path, extension, sha256 = _fetch_template_data(
        vit_connection,
        template_id
    )

    asset_file_path = _register_new_asset(
        vit_connection, package_path,
        asset_name, sha256, extension
    )

    vit_connection.create_dir_if_not_exists(os.path.dirname(asset_file_path))
    vit_connection.cp(template_path, asset_file_path)


def list_assets(local_path, package_path):
    tree_package, _ = tree_func.get_local_tree_package(
        local_path,
        package_path
    )
    with tree_package:
        ret = tree_package.list_assets()
    return ret


def get_asset_tree_info(local_path, package_path, asset_name):
    tree, _ = tree_func.get_local_tree_asset(
        local_path,
        package_path,
        asset_name
    )
    with tree:
        ret = tree.data
    return ret


def _fetch_template_data(vit_connection, template_id):
    vit_connection.get_vit_file(
        vit_connection.local_path,
        constants.VIT_TEMPLATE_CONFIG
    )
    with IndexTemplate(vit_connection.local_path) as index_template:
        template_data = index_template.get_template_path_from_id(template_id)
    if not template_data:
        raise Template_NotFound_E(template_id)
    template_path, sha256 = template_data
    extension = py_helpers.get_file_extension(template_path)
    return template_path, extension, sha256


def _create_tree_asset_file(local_path, tree_asset_path, asset_name):
    tree_asset_file_path_local = path_helpers.localize_path(
        local_path,
        tree_asset_path
    )
    tree_asset_file_dir_local = os.path.dirname(tree_asset_file_path_local)
    if not os.path.exists(tree_asset_file_dir_local):
        os.makedirs(tree_asset_file_dir_local)
    TreeAsset.create_file(tree_asset_file_path_local, asset_name)
    return TreeAsset(tree_asset_file_path_local)


def _register_new_asset(
        vit_connection, package_path,
        asset_name, sha256, extension):

    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    # raise packageNotFound
    tree_package, tree_package_path = tree_fetch.fetch_up_to_date_tree_package(
        vit_connection,
        package_path
    )

    asset_file_path = file_name_generation.generate_unique_asset_file_path(
        package_path,
        asset_name,
        extension
    )

    tree_asset_path = file_name_generation.generate_asset_tree_file_path(
        package_path,
        asset_name
    )

    with tree_package:
        if tree_package.get_asset_tree_file_path(asset_name) is not None:
            raise Asset_AlreadyExists_E(package_path, asset_name)
        tree_package.set_asset(asset_name, tree_asset_path)

    tree_asset = _create_tree_asset_file(
        vit_connection.local_path,
        tree_asset_path, asset_name
    )

    with tree_asset:
        tree_asset.add_commit(
            asset_file_path, None,
            time.time(), user,
            sha256, "asset created"
        )
        # TODO: PUBLISH !!!!!!
        tree_asset.set_branch("base", asset_file_path)
        tree_asset.set_root_commit(asset_file_path)

    vit_connection.put_auto(tree_package_path, tree_package_path)
    vit_connection.create_dir_if_not_exists(os.path.dirname(tree_asset_path))
    vit_connection.put_auto(tree_asset_path, tree_asset_path, recursive=True)

    return asset_file_path
