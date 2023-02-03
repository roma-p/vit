import time

from vit import py_helpers
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.vit_lib.misc import (
    file_name_generation,
    tree_fetch,
    tree_func
)
from vit.vit_lib import tag


def create_branch(
        local_path, vit_connection, package_path, asset_name, branch_new,
        branch_parent=None, commit_parent=None, create_tag=False):

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
        vit_connection, local_path,
        package_path, asset_name
    )

    with tree_asset:

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

        tree_asset.create_new_branch_from_commit(
            new_file_path,
            commit_parent,
            branch_new,
            time.time(),
            user
        )

        vit_connection.cp(commit_parent, new_file_path)

    vit_connection.put_auto(tree_asset_path, tree_asset_path)

    # FIXME : will require a "vit_connection"
    if create_tag:
        tag.create_tag_auto_from_branch(
            local_path, package_path,
            asset_name, branch_new,
            "first tag of branch", 1
        )


def list_branches(local_path, package_path, asset_name):
    tree_asset, _ = tree_func.get_local_tree_asset(
            local_path, package_path, asset_name)
    with tree_asset:
        branches = tree_asset.list_branches()
    return branches
