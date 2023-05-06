import time
from vit import py_helpers
from vit.vit_lib.misc import (
    tree_fetch,
    file_name_generation,
)
from vit.custom_exceptions import *
from vit.file_handlers import repo_config


def rebase_from_commit(
        vit_connection,
        package_path, asset_name,
        branch, commit_to_rebase_from):

    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)
    is_editor_of_file = False

    tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            vit_connection, package_path, asset_name,
    )

    with tree_asset:

        branch_current_commit = tree_asset.get_branch_current_file(branch)
        if not branch_current_commit:
            raise Branch_NotFound_E(asset_name, branch)

        commit_to_rebase_from_data = tree_asset.get_commit_data(commit_to_rebase_from)
        if not commit_to_rebase_from_data:
            raise Commit_NotFound_E(asset_name, commit_to_rebase_from)

        if not vit_connection.exists(commit_to_rebase_from):
            raise Path_FileNotFoundAtOrigin_E(
                commit_to_rebase_from,
                vit_connection.ssh_link
            )

        editor = tree_asset.get_editor(branch_current_commit)
        if editor is not None and editor != user:
            raise Asset_AlreadyEdited_E(asset_name, editor)
        if editor == user:
            is_editor_of_file = True
        else:
            tree_asset.set_editor(branch_current_commit, user)

    if not is_editor_of_file:
        vit_connection.put_auto(tree_asset_path, tree_asset_path)

    with tree_asset:
        extension = py_helpers.get_file_extension(commit_to_rebase_from)
        new_file_path = file_name_generation.generate_unique_asset_file_path(
            package_path, asset_name, extension
        )
        vit_connection.copy_file_at_origin(commit_to_rebase_from, new_file_path)
        tree_asset.add_commit(
            new_file_path,
            branch_current_commit,
            time.time(),
            user,
            commit_to_rebase_from_data["sha256"],
            "rebase branch from commit {}".format(commit_to_rebase_from)
        )
        tree_asset.set_branch(branch, new_file_path)
        if is_editor_of_file:
            tree_asset.set_editor(new_file_path, user)
        tree_asset.remove_editor(branch_current_commit)

    vit_connection.put_auto(tree_asset_path, tree_asset_path)
