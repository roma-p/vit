import time
from vit import py_helpers
from vit.file_handlers.tree_asset import TreeAsset
from vit.vit_lib.misc import (
    tree_fetch,
    tree_func,
    file_name_generation,
    tag_versionned_func
)
from vit.file_handlers import repo_config
from vit.custom_exceptions import *


def create_tag_light_from_branch(
        vit_connection,
        package_path, asset_name,
        branch, tag_name):

    # 1. checks and gather infos.

    if tag_versionned_func.check_is_auto_tag(tag_name):
        raise Tag_NameMatchVersionnedTag_E(tag_name)

    _, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
        vit_connection, package_path, asset_name
    )

    staged_asset_tree = vit_connection.get_metadata_from_origin_as_staged(
        tree_asset_path,
        TreeAsset
    )

    # 2. update origin metadata
    with vit_connection.lock_manager:

        with staged_asset_tree.file_handler as tree_asset:
            branch_ref = tree_asset.get_branch_current_file(branch)
            if not branch_ref:
                raise Branch_NotFound_E(asset_name, branch)
            if tree_asset.get_tag(tag_name):
                raise Tag_AlreadyExists_E(asset_name, tag_name)
            tree_asset.add_tag_lightweight(branch_ref, tag_name)

        vit_connection.put_metadata_to_origin(staged_asset_tree)


def create_tag_annotated_from_branch(
        vit_connection, package_path,
        asset_name, branch, tag_name, message):

    # 1. checks and gather infos.

    if tag_versionned_func.check_is_auto_tag(tag_name):
        raise Tag_NameMatchVersionnedTag_E(tag_name)

    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    _, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
        vit_connection,
        package_path,
        asset_name
    )

    staged_asset_tree = vit_connection.get_metadata_from_origin_as_staged(
        tree_asset_path,
        TreeAsset
    )

    with staged_asset_tree.file_handler as tree_asset:
        asset_parent_path = _get_asset_branch_file(
            tree_asset,
            asset_name,
            branch
        )

    new_file_path = file_name_generation.generate_unique_asset_file_path(
        package_path,
        asset_name,
        py_helpers.get_file_extension(asset_parent_path)
    )

    # 2. data transfer

    vit_connection.copy_file_at_origin(asset_parent_path, new_file_path)

    # 3. update origin metadata
    with vit_connection.lock_manager:
        with staged_asset_tree.file_handler as tree_asset:
            tree_asset.add_tag_annotated(
                asset_parent_path,
                new_file_path,
                tag_name, time.time(),
                user, message
            )
        vit_connection.put_metadata_to_origin(staged_asset_tree)


def create_tag_auto_from_branch(
        vit_connection, package_path,
        asset_name, branch, message, update_idx):

    # 1. checks and gather infos.

    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    _, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
        vit_connection,
        package_path,
        asset_name
    )

    staged_asset_tree = vit_connection.get_metadata_from_origin_as_staged(
        tree_asset_path,
        TreeAsset
    )

    with staged_asset_tree.file_handler as tree_asset:

        previous_auto_tag = tree_asset.get_last_auto_tag(branch)
        asset_parent_path = _get_asset_branch_file(
            tree_asset, asset_name, branch
        )

    if previous_auto_tag:
        version_numbers = list(
            tag_versionned_func.get_version_from_tag_auto(
                previous_auto_tag
            )
        )
    else:
        version_numbers = [0, 0, 0]

    version_numbers = tag_versionned_func.increment_version(
        update_idx,
        *version_numbers
    )

    tag_name = tag_versionned_func.generate_tag_auto_name_by_branch(
        asset_name,
        branch,
        *version_numbers
    )

    new_file_path = file_name_generation.generate_unique_asset_file_path(
        package_path,
        asset_name,
        py_helpers.get_file_extension(asset_parent_path)
    )

    # 2. data transfer
    vit_connection.copy_file_at_origin(asset_parent_path, new_file_path)

    # 3. update origin metadata
    with vit_connection.lock_manager:
        vit_connection.update_staged_metadata(staged_asset_tree)
        with staged_asset_tree.file_handler as tree_asset:
            tree_asset.set_last_auto_tag(branch, tag_name)
            tree_asset.add_tag_annotated(
                asset_parent_path,
                new_file_path,
                tag_name, time.time(),
                user, message
            )
        vit_connection.put_metadata_to_origin(staged_asset_tree)


def list_tags(local_path, package_path, asset_name):
    tree_asset, _ = tree_func.get_local_tree_asset(
            local_path, package_path, asset_name)
    with tree_asset:
        tags = tree_asset.list_tags()
    return tags


def list_auto_tags_by_branch(local_path, package_path, asset_name, branch):
    return tuple([
        t for t in list_tags(local_path, package_path, asset_name)
        if tag_versionned_func.check_is_auto_tag_of_branch(asset_name, branch, t)
    ])


# ----------------------------------------------------------------------------


def _get_asset_branch_file(tree_asset, asset_name,  branch):
    asset_file_path = tree_asset.get_branch_current_file(branch)
    if not asset_file_path:
        raise Branch_NotFound_E(asset_name, branch)
    return asset_file_path
