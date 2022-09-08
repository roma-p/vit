import time

from vit import py_helpers
from vit import path_helpers
from vit import constants

from vit.file_handlers import repo_config
from vit.file_handlers.index_template import IndexTemplate
from vit.file_handlers.index_tracked_file import IndexTrackedFile
from vit.file_handlers.index_package import IndexPackage

from vit.file_handlers.tree_package import TreePackage
from vit.file_handlers.tree_asset import TreeAsset

from vit.connection.vit_connection import VitConnection, ssh_connect_auto
from vit.custom_exceptions import *


def commit_file(local_path, checkout_file, commit_mess,
                keep_file=False, keep_editable=False):

    file_track_data = get_file_track_data(local_path, checkout_file)
    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = fetch_tree.fetch_up_to_date_tree_asset(
                ssh_connection,
                local_path,
                file_track_data["package_path"],
                file_track_data["asset_name"]
        )

        with tree_asset:

            raise_if_file_is_not_to_commit(
                file_track_data, tree_asset,
                user, checkout_file
            )

            new_file_path = file_name_generation.generate_unique_asset_file_path(
                file_track_data["package_path"],
                file_track_data["asset_name"],
                py_helpers.get_file_extension(checkout_file)
            )

            tree_asset.update_on_commit(
                path_helpers.localize_path(local_path, checkout_file),
                new_file_path,
                file_track_data["origin_file_name"],
                time.time(),
                user,
                commit_mess,
                keep_editable
            )

        ssh_connection.put_auto(checkout_file, new_file_path)
        ssh_connection.put_auto(tree_asset_path, tree_asset_path)

    if not keep_file:
        remove_tracked_file(local_path, checkout_file)


# -----------------------------------------------------------------------------


def get_file_track_data(local_path, checkout_file):

    with IndexTrackedFile(local_path) as index_tracked_file:
        file_data = index_tracked_file.get_files_data(local_path)
    if checkout_file not in file_data:
        raise Asset_UntrackedFile_E(checkout_file)
    return file_data[checkout_file]


def raise_if_file_is_not_to_commit(file_track_data, tree_asset_open,
                                   user, checkout_file):
    if not file_track_data["changes"]:
        raise Asset_NoChangeToCommit_E(checkout_file)
    if tree_asset_open.get_editor(file_track_data["origin_file_name"]) != user:
        raise Asset_NotEditable_E(checkout_file)
    if not tree_asset_open.get_branch_from_file(file_track_data["origin_file_name"]):
        raise Asset_NotAtTipOfBranch(checkout_file, "FIXME blabla")


def remove_tracked_file(local_path, checkout_file):
    os.remove(path_helpers.localize_path(local_path, checkout_file))
    with IndexTrackedFile(local_path) as index_tracked_file:
        index_tracked_file.remove_file(checkout_file)
