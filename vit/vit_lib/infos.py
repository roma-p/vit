from vit.custom_exceptions import *
from vit.file_handlers.repo_config import RepoConfig
from vit.connection.vit_connection import ssh_connect_auto
from vit.vit_lib.misc import (
    tree_func,
    tracked_file_func
)


def get_info_from_ref_file(local_path, checkout_file):

    file_track_data = tracked_file_func.get_file_track_data(local_path,
                                                            checkout_file)
    with RepoConfig(local_path) as config:
        last_fetch = config.get_last_fetch_time()
        _, _, user = config.get_origin_ssh_info()

    file_track_data["editable"] = is_file_editable_by_user(
        local_path, file_track_data, user
    )
    file_track_data["last_fetch"] = last_fetch
    return file_track_data


def get_info_from_all_ref_files(local_path):
    tracked_info = tracked_file_func.get_all_files_track_data(local_path)

    with RepoConfig(local_path) as repo_config:
        last_fetch = repo_config.get_last_fetch_time()
        _, _, user = repo_config.get_origin_ssh_info()

    output_dict = {
        "last_fetch": last_fetch,
        "editable": {},
        "readonly": {}
    }

    for file_path, data in tracked_info.items():

        editable = is_file_editable_by_user(
            local_path, data, user
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


def is_file_editable_by_user(local_path, file_track_data, user):
    tree_asset, _ = tree_func.get_local_tree_asset(
        local_path,
        file_track_data["package_path"],
        file_track_data["asset_name"]
    )
    with tree_asset:
        ret = tree_asset.get_editor(file_track_data["origin_file_name"]) == user
    return ret
