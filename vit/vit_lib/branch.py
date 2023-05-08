import time

from vit import py_helpers
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.file_handlers.tree_asset import TreeAsset
from vit.vit_lib.misc import (
    file_name_generation,
    tree_fetch,
    tree_func
)
from vit.vit_lib import tag


def create_branch(
        vit_connection, package_path, asset_name, branch_new,
        branch_parent=None, commit_parent=None, create_tag=False):

    # 1. checks and gather infos.

    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    _, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
        vit_connection, package_path, asset_name
    )

    staged_asset_tree = vit_connection.get_metadata_from_origin_as_staged(
        tree_asset_path,
        TreeAsset
    )

    with staged_asset_tree.file_handler as tree_asset:

        if branch_parent:
            commit_parent = tree_asset.get_branch_current_file(branch_parent)
            if commit_parent is None:
                raise Branch_NotFound_E(asset_name, branch_parent)
        elif commit_parent:
            commit_parent = tree_asset.get_commit(commit_parent)
            if commit_parent is None:
                raise Commit_NotFound_E(asset_name, commit_parent)
        else:
            raise ValueError("missing argument: either branch_parent or commit_parent")

        if tree_asset.get_branch_current_file(branch_new):
            raise Branch_AlreadyExist_E(asset_name, branch_new)

        extension = py_helpers.get_file_extension(commit_parent)

    new_file_path = file_name_generation.generate_unique_asset_file_path(
        package_path,
        asset_name,
        extension
    )

    # 2. data transfer.

    vit_connection.copy_file_at_origin(commit_parent, new_file_path)

    # 3. update origin metadatas
    # TODO : with vit_connection.lock:

    vit_connection.update_staged_metadata(staged_asset_tree)

    with staged_asset_tree.file_handler as tree_asset:

        if tree_asset.get_branch_current_file(branch_new):
            raise Branch_AlreadyExist_E(asset_name, branch_new)

        tree_asset.create_new_branch_from_commit(
            new_file_path,
            commit_parent,
            branch_new,
            time.time(),
            user
        )

    vit_connection.put_metadata_to_origin(staged_asset_tree)

    # 4. misc.

    # FIXME : will require a "vit_connection"
    if create_tag:
        tag.create_tag_auto_from_branch(
            vit_connection, package_path,
            asset_name, branch_new,
            "first tag of branch", 1
        )


def list_branches(local_path, package_path, asset_name):
    tree_asset, _ = tree_func.get_local_tree_asset(
            local_path, package_path, asset_name)
    with tree_asset:
        branches = tree_asset.list_branches()
    return branches
