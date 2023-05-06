import time
from vit import path_helpers
from vit import py_helpers
from vit.vit_lib.misc import (
    tree_func, tree_fetch,
    file_name_generation,
    tracked_file_func
)
from vit.custom_exceptions import *
from vit.file_handlers import repo_config


def commit_file_new(
    vit_connection, checkout_file, commit_mess,
    keep_file=False, keep_editable=False):

    file_track_data = tracked_file_func.get_file_track_data(
        vit_connection.local_path,
        checkout_file
    )
    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            vit_connection,
            file_track_data["package_path"],
            file_track_data["asset_name"]
    )

    with tree_asset:

        _raise_if_file_is_not_to_commit(
            file_track_data, tree_asset,
            user, checkout_file
        )

        new_file_path = file_name_generation.generate_unique_asset_file_path(
            file_track_data["package_path"],
            file_track_data["asset_name"],
            py_helpers.get_file_extension(checkout_file)
        )

    transfer_data = ((checkout_file, new_file_path, keep_editable),)

    def hook_process_metadata():
        staged_tree_asset, stage_tree_asset_path = create_stage_metadata(tree_asset_path)
        with staged_tree_asset.metadata:
            staged_tree_asset.update_on_commit(
                path_helpers.localize_path(vit_connection.local_path, checkout_file),
                new_file_path,
                file_track_data["origin_file_name"],
                time.time(),
                user,
                commit_mess,
                keep_editable
            )
        return staged_tree_asset

    Transaction(transfer_data, hook_process_metadata).run()


def commit_file(vit_connection, checkout_file,
                commit_mess, keep_file=False, keep_editable=False):

    file_track_data = tracked_file_func.get_file_track_data(
        vit_connection.local_path,
        checkout_file
    )
    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            vit_connection,
            file_track_data["package_path"],
            file_track_data["asset_name"]
    )

    with tree_asset:

        _raise_if_file_is_not_to_commit(
            file_track_data, tree_asset,
            user, checkout_file
        )

        new_file_path = file_name_generation.generate_unique_asset_file_path(
            file_track_data["package_path"],
            file_track_data["asset_name"],
            py_helpers.get_file_extension(checkout_file)
        )

        tree_asset.update_on_commit(
            path_helpers.localize_path(vit_connection.local_path, checkout_file),
            new_file_path,
            file_track_data["origin_file_name"],
            time.time(),
            user,
            commit_mess,
            keep_editable
        )

    vit_connection.put_data_to_origin(checkout_file, new_file_path)
    vit_connection.put_auto(tree_asset_path, tree_asset_path)

    if not keep_file:
        tracked_file_func.remove_tracked_file(
            vit_connection.local_path,
            checkout_file
        )
    else:
        tracked_file_func.update_tracked_file(
            vit_connection.local_path,
            checkout_file, new_file_path)
    return new_file_path

# FIXME: does this need to be done offline? with local cache like other listing?
def list_commits(local_path, package_path, asset_name):
    tree_asset, _ = tree_func.get_local_tree_asset(
            local_path, package_path, asset_name)
    with tree_asset:
        commits = tree_asset.list_commits()
    return commits


def release_editable(vit_connection, checkout_file):

    file_track_data = tracked_file_func.get_file_track_data(
        vit_connection.local_path,
        checkout_file
    )
    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            vit_connection,
            file_track_data["package_path"],
            file_track_data["asset_name"]
    )

    with tree_asset:
        if tree_asset.get_editor(file_track_data["origin_file_name"]) != user:
            raise Asset_NotEditable_E(checkout_file)
        tree_asset.remove_editor(file_track_data["origin_file_name"])

    vit_connection.put_auto(tree_asset_path, tree_asset_path)

# -----------------------------------------------------------------------------

def _raise_if_file_is_not_to_commit(file_track_data, tree_asset_open,
                                   user, checkout_file):
    if not file_track_data["changes"]:
        raise Asset_NoChangeToCommit_E(checkout_file)
    if tree_asset_open.get_editor(file_track_data["origin_file_name"]) != user:
        raise Asset_NotEditable_E(checkout_file)
    if not tree_asset_open.get_branch_from_file(file_track_data["origin_file_name"]):
        raise Asset_NotAtTipOfBranch(checkout_file, "can't commit file not at tip of branch!")
