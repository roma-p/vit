import os
from vit import constants
from vit import path_helpers
from vit.vit_lib.misc import file_name_generation
from vit.custom_exceptions import *
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_package import TreePackage


def create_package(
        local_path, vit_connection,
        package_path, force_subtree=False):

    origin_package_dir = package_path
    origin_parent_dir = os.path.dirname(origin_package_dir)

    vit_connection.get_vit_file(local_path, constants.VIT_PACKAGES)
    with IndexPackage(local_path) as package_index:
        if package_index.check_package_exists(package_path):
            raise Package_AlreadyExists_E(package_path)

        package_asset_file_name = file_name_generation.generate_package_tree_file_name(
            package_path
        )
        package_asset_file_path = os.path.join(
            constants.VIT_DIR,
            constants.VIT_ASSET_TREE_DIR,
            package_asset_file_name
        )
        package_asset_file_local_path = path_helpers.localize_path(
            local_path,
            package_asset_file_path
        )

        if not vit_connection.exists(origin_parent_dir):
            if not force_subtree:
                raise Path_ParentDirNotExist_E(origin_parent_dir)

        package_index.set_package(package_path, package_asset_file_path)
        TreePackage.create_file(package_asset_file_local_path, package_path)
        vit_connection.mkdir(origin_package_dir, p=True)

    vit_connection.put_vit_file(local_path, constants.VIT_PACKAGES)
    vit_connection.put_auto(
        package_asset_file_path,
        package_asset_file_path,
        recursive=True
    )


def list_packages(local_path):
    with IndexPackage(local_path) as package_index:
        ret = package_index.list_packages()
    return ret
