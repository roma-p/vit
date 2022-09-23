from vit.custom_exceptions import *
from vit.vit_lib.checkout_datatypes import CheckoutType
from vit.connection.vit_connection import ssh_connect_auto
from vit.file_handlers import repo_config
from vit.vit_lib.misc import (
    tracked_file_func,
    tree_func, tree_fetch
)

def update(local_path, checkout_file, editable=False, reset=False):

    file_track_data = tracked_file_func.get_file_track_data(local_path, checkout_file)
    _, _, user = repo_config.get_origin_ssh_info(local_path)

    asset_name = file_track_data["asset_name"]
    package_path = file_track_data["package_path"]
    checkout_type = file_track_data["checkout_type"]
    branch = file_track_data["checkout_value"]
    changes = file_track_data["changes"]

    if checkout_type != CheckoutType.branch:
        raise Asset_UpdateOnNonBranchCheckout_E(checkout_type)

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path, asset_name
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
                        ssh_connection.get_auto(commit_origin, checkout_file)
                else:
                    if not changes or changes and reset:
                        tree_func.become_editor_of_asset(
                            tree_asset, asset_name,
                            commit_origin, user
                        )
                        ssh_connection.get_auto(commit_origin, checkout_file)
                    else:
                        raise Asset_ChangeNotCommitted_E(asset_name)
            else:

                if not changes and checkout_at_last_commit:
                    raise Asset_AlreadyUpToDate_E(asset_name)

                elif changes and not reset:
                    raise Asset_ChangeNotCommitted_E(asset_name)

                else:
                    ssh_connection.get_auto(commit_origin, checkout_file)

        ssh_connection.put_auto(tree_asset_path, tree_asset_path)

    tracked_file_func.update_tracked_file(local_path, checkout_file, commit_origin)

