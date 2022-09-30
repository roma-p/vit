from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.file_handlers.index_tracked_file import IndexTrackedFile
from vit.connection.vit_connection import ssh_connect_auto
from vit.vit_lib.misc import (
    tree_fetch,
    tracked_file_func
)

def get_info_from_ref_file(local_path, checkout_file):

    file_track_data = tracked_file_func.get_file_track_data(local_path, checkout_file)
    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, _ = tree_fetch.fetch_up_to_date_tree_asset(
                ssh_connection,
                local_path,
                file_track_data["package_path"],
                file_track_data["asset_name"]
        )

        with tree_asset:
            if tree_asset.get_editor(file_track_data["origin_file_name"]) == user:
                file_track_data["editable"] = True
            else:
                file_track_data["editable"] = False
    return file_track_data
