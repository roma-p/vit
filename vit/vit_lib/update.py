from vit.custom_exceptions import *
from vit.vit_lib.checkout_datatypes import CheckoutType
from vit.file_handlers import repo_config
from vit.vit_lib.misc import (
    tracked_file_func,
    tree_func, tree_fetch
)


def update(vit_connection, checkout_file, editable=False, reset=False):

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

    tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
        vit_connection, package_path, asset_name
    )

    with tree_asset:

        commit_origin = tree_asset.get_branch_current_file(branch)
        checkout_at_last_commit = commit_origin == file_track_data["origin_file_name"]

        if editable:
            if checkout_at_last_commit:
                tree_func.become_editor_of_asset(
                    tree_asset, asset_name,
                    commit_origin, user
                )
                if reset:
                    get_file_from_origin = True
                else:
                    update_sha = False
            else:
                if not changes or changes and reset:
                    tree_func.become_editor_of_asset(
                        tree_asset, asset_name,
                        commit_origin, user
                    )
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
    if get_file_from_origin:
        vit_connection.get_data_from_origin(
            commit_origin,
            checkout_file,
            is_editable=editable
        )
    vit_connection.put_auto(tree_asset_path, tree_asset_path)

    tracked_file_func.update_tracked_file(
        vit_connection.local_path,
        checkout_file,
        commit_origin,
        update_sha
    )
