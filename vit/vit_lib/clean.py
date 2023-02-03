import os
from vit import path_helpers
from vit.vit_lib.misc import tree_func
from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.file_handlers.index_tracked_file import IndexTrackedFile


def get_files_to_clean(local_path):

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    file_to_clean = []
    file_editable = []
    file_non_editable_but_changed = []

    with IndexTrackedFile(local_path) as index_tracked_file:
        all_track_data = index_tracked_file.get_files_data(local_path)

    for checkout_file, track_data in all_track_data.items():
        if not _is_file_editable_by_user(
                local_path,
                track_data,
                user):
            if track_data["changes"]:
                file_non_editable_but_changed.append(checkout_file)
            else:
                file_to_clean.append(checkout_file)
        else:
            file_editable.append(checkout_file)
    return {
        "to_clean": tuple(file_to_clean),
        "editable": tuple(file_editable),
        "changes": tuple(file_non_editable_but_changed)
    }


def clean_files(local_path, *file_list):
    with IndexTrackedFile(local_path) as index_tracked_file:
        for file in file_list:
            index_tracked_file.remove_file(file)
            os.remove(path_helpers.localize_path(local_path, file))


# -----------------------------------------------------------------------------

def _is_file_editable_by_user(local_path, file_track_data, user):
    tree_asset, _ = tree_func.get_local_tree_asset(
        local_path,
        file_track_data["package_path"],
        file_track_data["asset_name"]
    )
    with tree_asset:
        ret = tree_asset.get_editor(file_track_data["origin_file_name"]) == user
    return ret
