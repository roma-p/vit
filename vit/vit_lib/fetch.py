from vit import constants
from vit import path_helpers
from vit.vit_lib.misc import file_name_generation
from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_package import TreePackage
from vit.file_handlers.tree_asset import TreeAsset

def fetch(local_path):
    with ssh_connect_auto(local_path) as sshConnection:
        sshConnection.fetch_vit()

def get_repo_hierarchy(local_path):
    ret = {}
    with IndexPackage(local_path) as package_index:
        package_path_list = sorted(package_index.list_packages())
    for package_path in package_path_list:
        single_package_list = package_path.split("/")
        dict_to_update = ret
        for i in range(len(single_package_list) - 1):
            dict_to_update = dict_to_update[single_package_list[i]]["packages"]
        dict_to_update[single_package_list[-1]] = {
            "packages": {},
            "assets": {}
        }

        tree_package_path = path_helpers.localize_path(
            local_path,
            file_name_generation.generate_package_tree_file_path(package_path)
        )
        with TreePackage(tree_package_path) as tree_package:
            dict_to_update[single_package_list[-1]]["assets"] = tree_package.list_assets()
    return ret

def get_all_assets_info(local_path):
    ret = {}
    with IndexPackage(local_path) as package_index:
        package_list = package_index.list_packages()
    for package_path in package_list:
        ret[package_path] = {}
        tree_package_path = path_helpers.localize_path(
            local_path,
            file_name_generation.generate_package_tree_file_path(package_path)
        )
        with TreePackage(tree_package_path) as tree_package:
            asset_list = tree_package.list_assets()
            for asset in asset_list:
                asset_tree_path = path_helpers.localize_path(
                    local_path,
                    file_name_generation.generate_asset_tree_file_path(
                        package_path, asset
                    )
                )
                with TreeAsset(asset_tree_path) as tree_asset:
                    ret[package_path][asset] = tree_asset.data
    return ret

def get_all_file_track_data(local_path):
    with IndexTrackedFile(local_path) as index_tracked_file:
        track_data = index_tracked_file.get_files_data(local_path)
    return track_data

