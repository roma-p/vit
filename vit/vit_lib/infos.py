from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.connection.vit_connection import ssh_connect_auto
from vit.vit_lib.misc import (
    tree_fetch,
    tracked_file_func
)


def get_info_from_ref_file(local_path, checkout_file):

    file_track_data = tracked_file_func.get_file_track_data(local_path, checkout_file)
    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with ssh_connect_auto(local_path) as ssh_connection:
        file_track_data["editable"] = is_file_editable_by_user(
            local_path, file_track_data, user
        )
    return file_track_data


def get_info_from_all_ref_files(local_path):
    tracked_info = tracked_file_func.get_all_files_track_data(local_path)
    _, _, user = repo_config.get_origin_ssh_info(local_path)
    output_dict = {
        "editable": {},
        "readonly": {}
    }

    with ssh_connect_auto(local_path) as ssh_connection:
        for file_path, data in tracked_info.items():

            editable = is_file_editable_by_user(
                local_path, ssh_connection, data, user
            )

            dict_key = "editable" if editable else "readonly"
            dict_level1 = output_dict[dict_key]

            package = data.get("package_path")
            if package not in dict_level1:
                dict_level1[package] = {}
            package_dict = dict_level1[package]

            asset = data.get("asset_name")
            if asset not in package_dict:
                package_dict[asset] = {}
            asset_dict = package_dict[asset]

            asset_dict[file_path] = {
                "editable": editable,
                "checkout_type": data["checkout_type"],
                "checkout_value": data["checkout_value"],
                "changes": data["changes"]
            }
    return output_dict


def is_file_editable_by_user(local_path, ssh_connection, file_track_data, user):
    tree_asset, _ = tree_fetch.fetch_up_to_date_tree_asset(
        ssh_connection,
        local_path,
        file_track_data["package_path"],
        file_track_data["asset_name"]
    )
    with tree_asset:
        ret =  tree_asset.get_editor(file_track_data["origin_file_name"]) == user
    return ret
