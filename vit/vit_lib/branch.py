import time

from vit import py_helpers
from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.vit_lib.misc import (
    file_name_generation,
    tree_fetch
)
from vit.vit_lib import tag

def branch_from_origin_branch(
        local_path, package_path,
        asset_name, branch_parent,
        branch_new, create_tag=False):

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )

        with tree_asset:

            branch_ref = tree_asset.get_branch_current_file(branch_parent)
            if branch_ref is None:
                raise Branch_NotFound_E(asset_name, branch_parent)

            if tree_asset.get_branch_current_file(branch_new):
                raise Branch_AlreadyExist_E(asset_name, branch_new)

            extension = py_helpers.get_file_extension(branch_ref)
            new_file_path = file_name_generation.generate_unique_asset_file_path(
                package_path,
                asset_name,
                extension
            )

            tree_asset.create_new_branch_from_file(
                new_file_path,
                branch_parent,
                branch_new,
                time.time(),
                user
            )

            ssh_connection.cp(branch_ref, new_file_path)

        ssh_connection.put_auto(tree_asset_path, tree_asset_path)

    if create_tag:
        tag.create_tag_auto_from_branch(
            local_path, package_path,
            asset_name, branch_new,
            "first tag of branch", 1
        )

def list_branches(local_path, package_path, asset_name):
    with ssh_connect_auto(local_path) as ssh_connection:
        tree_asset, _ = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )
        with tree_asset:
           branches = tree_asset.list_branches()
    return branches

