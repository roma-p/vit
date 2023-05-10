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
from vit.file_handlers.tree_package import TreePackage


def create_asset_from_file(
        vit_connection, package_path,
        asset_name, file_path):

    # 1. checks and gather info
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        raise Path_FileNotFound_E(file_path)
    sha256 = py_helpers.calculate_file_sha(file_path)
    extension = py_helpers.get_file_extension(file_path)

    staged_tree_package = _get_staged_tree_package(vit_connection, package_path)
    _check_asset_already_exists(staged_tree_package, package_path, asset_name)

    asset_file_path = file_name_generation.generate_unique_asset_file_path(
        package_path,
        asset_name,
        extension
    )

    # 2. data transfer

    vit_connection.create_dir_at_origin_if_not_exists(
        os.path.dirname(asset_file_path)
    )
    vit_connection.put_data_to_origin(
        file_path, asset_file_path,
        is_src_abritrary_path=True
    )

    # 3. update origin metadata

    _update_origin_metadata(
        vit_connection, staged_tree_package, package_path,
        asset_name, asset_file_path, sha256, extension)


def create_asset_from_template(
        vit_connection, package_path,
        asset_name, template_id):

    # 1. checks and gather info

    template_path, extension, sha256 = _fetch_template_data(
        vit_connection,
        template_id
    )

    staged_tree_package = _get_staged_tree_package(vit_connection, package_path)
    _check_asset_already_exists(staged_tree_package, package_path, asset_name)

    asset_file_path = file_name_generation.generate_unique_asset_file_path(
        package_path,
        asset_name,
        extension
    )

    # 2. data transfer

    vit_connection.create_dir_at_origin_if_not_exists(
        os.path.dirname(asset_file_path)
    )
    vit_connection.copy_file_at_origin(template_path, asset_file_path)

    # 3. update origin metadata

    _update_origin_metadata(
        vit_connection, staged_tree_package, package_path,
        asset_name, asset_file_path, sha256, extension)


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

# - PRIVATE ------------------------------------------------------------------


def _fetch_template_data(vit_connection, template_id):
    vit_connection.get_metadata_from_origin(constants.VIT_TEMPLATE_CONFIG)
    with IndexTemplate.get_index_template(vit_connection.local_path) as index_template:
        template_data = index_template.get_template_path_from_id(template_id)
    if not template_data:
        raise Template_NotFound_E(template_id)
    template_path, sha256 = template_data
    extension = py_helpers.get_file_extension(template_path)
    return template_path, extension, sha256


def _get_staged_tree_package(vit_connection, package_path):
    # TODO : func to get it as staged automatically...
    _, tree_package_path = tree_fetch.fetch_up_to_date_tree_package(
        vit_connection,
        package_path
    )
    staged_tree_package = vit_connection.get_metadata_from_origin_as_staged(
        tree_package_path,
        TreePackage
    )
    return staged_tree_package


def _check_asset_already_exists(staged_tree_package, package_path, asset_name):
    with staged_tree_package.file_handler as tree_package:
        if tree_package.get_asset_tree_file_path(asset_name) is not None:
            raise Asset_AlreadyExists_E(package_path, asset_name)


def _update_origin_metadata(
        vit_connection, stage_package, package_path,
        asset_name, asset_file_path, sha256, extension):

    with vit_connection.lock_manager:

        vit_connection.update_staged_metadata(stage_package)

        _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

        tree_asset_path = file_name_generation.generate_asset_tree_file_path(
            package_path,
            asset_name
        )

        with stage_package.file_handler as tree_package:
            tree_package.set_asset(asset_name, tree_asset_path)

        stage_asset = tree_func.create_metadata_file_as_stage(
            vit_connection.local_path,
            tree_asset_path,
            TreeAsset,
            asset_name=asset_name
        )

        with stage_asset.file_handler as tree_asset:
            tree_asset.add_commit(
                asset_file_path, None,
                time.time(), user,
                sha256, "asset created"
            )
            # TODO: PUBLISH !!!!!!
            tree_asset.set_branch("base", asset_file_path)
            tree_asset.set_root_commit(asset_file_path)

        vit_connection.create_dir_at_origin_if_not_exists(
            os.path.dirname(tree_asset_path)
        )
        vit_connection.put_metadata_to_origin(stage_package)
        vit_connection.put_metadata_to_origin(stage_asset, recursive=True)
