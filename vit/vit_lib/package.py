import os
from vit import constants
from vit.custom_exceptions import *
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_package import TreePackage
from vit.vit_lib.misc import tree_func, file_name_generation


def create_package(vit_connection, package_path, force_subtree=False):

    with vit_connection.lock_manager:

        origin_package_dir = package_path
        origin_parent_dir = os.path.dirname(origin_package_dir)

        vit_connection.get_metadata_from_origin(constants.VIT_PACKAGES)
        staged_index = vit_connection.get_metadata_from_origin_as_staged(
            constants.VIT_PACKAGES,
            IndexPackage
        )

        with staged_index.file_handler as package_index:
            if package_index.check_package_exists(package_path):
                raise Package_AlreadyExists_E(package_path)

            package_asset_file_name = file_name_generation.generate_package_tree_file_name(
                package_path
            )
            package_asset_file_path = os.path.join(
                constants.VIT_ASSET_TREE_DIR,
                package_asset_file_name
            )

            if not vit_connection.exists_on_origin(origin_parent_dir):
                if not force_subtree:
                    raise Path_ParentDirNotExist_E(origin_parent_dir)

            package_index.set_package(package_path, package_asset_file_path)

            stage_package = tree_func.create_metadata_file_as_stage(
                vit_connection.local_path,
                package_asset_file_path,
                TreePackage,
                package_name=package_path
            )

            vit_connection.create_dir_at_origin_if_not_exists(origin_package_dir)

        vit_connection.put_metadata_to_origin(staged_index)
        vit_connection.put_metadata_to_origin(stage_package, recursive=True)


def list_packages(local_path):
    with IndexPackage.get_local_index_package(local_path) as package_index:
        ret = package_index.list_packages()
    return ret
