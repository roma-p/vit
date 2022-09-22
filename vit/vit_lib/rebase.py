import time
from vit import py_helpers
from vit.vit_lib.misc import (
    tree_fetch,
    file_name_generation,
)
from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.file_handlers import repo_config

def rebase_from_commit(
        local_path, package_path, asset_name,
        branch, commit_to_rebase_from):

    _, _, user = repo_config.get_origin_ssh_info(local_path)
    is_not_editor_of_file = False

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
                ssh_connection, local_path,
                package_path, asset_name,
        )

        with tree_asset:

            branch_current_commit = tree_asset.get_branch_current_file(branch)
            if not branch_current_commit:
                raise Branch_NotFound_E(asset_name, branch)
            branch_current_commit_data = tree_asset.get_commit_data(branch_current_commit)

            commit_to_rebase_from_data = tree_asset.get_commit_data(commit_to_rebase_from)
            if not commit_to_rebase_from_data:
                raise Commit_NotFound_E(asset_name, commit_to_rebase_from)

            if not ssh_connection.exists(commit_to_rebase_from):
                raise Path_FileNotFoundAtOrigin_E(
                    commit_to_rebase_from,
                    ssh_connection.ssh_link
                )

            editor = tree_asset.get_editor(branch_current_commit)
            if editor and editor != user:
                raise Asset_AlreadyEdited_E(asset_name, editor)

            if editor is None:
                is_not_editor_of_file = True
                tree_asset.set_editor(branch_current_commit, user)

        if is_not_editor_of_file:
            ssh_connection.put_auto(tree_asset_path, tree_asset_path)

        with tree_asset:
            extension = py_helpers.get_file_extension(commit_to_rebase_from)
            new_file_path = file_name_generation.generate_unique_asset_file_path(
                package_path, asset_name, extension
            )
            ssh_connection.cp(commit_to_rebase_from, new_file_path)
            tree_asset.add_commit(
                new_file_path,
                branch_current_commit_data["parent"],
                time.time(),
                user,
                commit_to_rebase_from_data["sha256"],
                "rebase branch from commit {}".format(commit_to_rebase_from)
            )
            if is_not_editor_of_file:
                tree_asset.set_editor(new_file_path, user)

        ssh_connection.put_auto(tree_asset_path, tree_asset_path)
