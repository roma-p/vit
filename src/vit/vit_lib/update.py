from vit.custom_exceptions import *
from vit.vit_lib.checkout_datatypes import CheckoutType
from vit.file_handlers import repo_config
from vit.vit_lib.misc import (
    tracked_file_func,
    tree_func, tree_fetch
)


def update(vit_connection, checkout_file, editable=False, reset=False):

    # 1. checks and gather infos.

    file_track_data = tracked_file_func.get_file_track_data(
        vit_connection.local_path, checkout_file
    )
    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    asset_name = file_track_data["asset_name"]
    package_path = file_track_data["package_path"]
    checkout_type = file_track_data["checkout_type"]
    branch = file_track_data["checkout_value"]
    changes = file_track_data["changes"]

    update_sha = True
    get_file_from_origin = False

    if checkout_type != CheckoutType.branch:
        raise Asset_UpdateOnNonBranchCheckout_E(checkout_type)

    staged_asset_tree = tree_fetch.fetch_up_to_date_stage_tree_asset(
        vit_connection, package_path, asset_name
    )

    shall_become_editor = False

    with staged_asset_tree.file_handler as tree_asset:
        commit_origin = tree_asset.get_branch_current_file(branch)

    checkout_at_last_commit = commit_origin == file_track_data["origin_file_name"]

    # TODO: REFACTO ME !
    # if editable: have to get file from origin.
    # (because vit_connection local mode.
    # ONLY TRUE IF FILE IS NOT ALREADY EDITABLE.

    if editable:
        if checkout_at_last_commit:
            shall_become_editor = True
            if reset:
                get_file_from_origin = True
            else:
                update_sha = False
        else:
            if not changes or changes and reset:
                shall_become_editor = True
                get_file_from_origin = True
            else:
                raise Asset_ChangeNotCommitted_E(asset_name)
    else:
        if checkout_at_last_commit:
            if reset and changes:
                get_file_from_origin = True
            else:
                raise Asset_AlreadyUpToDate_E(asset_name)
        else:
            if reset or not changes:
                get_file_from_origin = True
            else:
                raise Asset_ChangeNotCommitted_E(asset_name)

    # 2. data transfer

    if get_file_from_origin or editable:
        vit_connection.get_data_from_origin(
            commit_origin,
            checkout_file,
            is_editable=editable
        )

    # 3. update origin metadata.

    with vit_connection.lock_manager:
        if shall_become_editor:
            vit_connection.update_staged_metadata(staged_asset_tree)
            with staged_asset_tree.file_handler as tree_asset:
                tree_func.become_editor_of_asset(
                    tree_asset, asset_name,
                    commit_origin, user
                )
            vit_connection.put_metadata_to_origin(staged_asset_tree)
        else:
            staged_asset_tree.remove_stage_metadata()

    # 4. update local metadata.

    tracked_file_func.update_tracked_file(
        vit_connection.local_path,
        checkout_file,
        commit_origin,
        update_sha
    )
