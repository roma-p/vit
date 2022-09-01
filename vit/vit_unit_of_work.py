import os
from vit import path_helpers
from vit import constants
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.tree_package import TreePackage
from vit.file_handlers.index_tracked_file import IndexTrackedFile
from vit.file_handlers import repo_config
from vit.custom_exceptions import *

# ----

def fetch_asset_file_tree(ssh_connection, path, package_path, asset_name):
    tree_asset_file_path = _get_asset_file_tree(
            ssh_connection, path,
            package_path, asset_name
    )
    tree_asset_file_path_local = path_helpers.localize_path(
        path,
        tree_asset_file_path
    )
    tree_asset_dir_path_local = os.path.dirname(tree_asset_file_path_local)
    if not os.path.exists(tree_asset_dir_path_local):
        os.makedirs(tree_asset_dir_path_local)
    ssh_connection.get(tree_asset_file_path, tree_asset_file_path_local)
    return tree_asset_file_path


def _get_asset_file_tree(ssh_connection, path, package_path, asset_name):
    # refacto me.

    ssh_connection.get_vit_file(path, constants.VIT_PACKAGES)

    with IndexPackage(path) as package_index:
        package_file_name = package_index.get_package_tree_file_path(package_path)
    if not package_file_name:
        raise Package_AlreadyExists_E(package_path)

    ssh_connection.get(
        package_file_name,
        path_helpers.localize_path(path, package_file_name)
    )

    with TreePackage(os.path.join(path, package_file_name)) as tree_package:
        asset_file_tree_path = tree_package.get_asset_tree_file_path(asset_name)
    if not asset_file_tree_path:
        raise Asset_NotFound_E(package_path, asset_name)

    if not os.path.exists(
            path_helpers.localize_path(
                path,
                os.path.dirname(asset_file_tree_path)
            )):
        os.makedirs(
            path_helpers.localize_path(
                path, 
                os.path.dirname(asset_file_tree_path)
            )
        )

    ssh_connection.get(
        asset_file_tree_path,
        os.path.join(path, asset_file_tree_path)
    )
    return asset_file_tree_path

# ----

def get_asset_file_path_by_branch(ssh_connection, tree_asset, 
                                  asset_name, branch): 
    asset_filepath = tree_asset.get_branch_current_file(branch)
    if not asset_filepath:
        raise Branch_NotFound_E(asset_name, branch)
    if not ssh_connection.exists(asset_filepath):
        raise Path_FileNotFoundAtOrigin_E(
            asset_filepath,
            ssh_connection.ssh_link
        )
    return asset_filepath

# ----

def become_editor_of_asset(tree_asset, asset_name, asset_filepath, user):
    editor = tree_asset.get_editor(asset_filepath)
    if editor:
        raise Asset_AlreadyEdited_E(asset_name, editor)
    tree_asset.set_editor(asset_filepath, user)

# ----

def check_if_file_is_to_commit(vit_repo_local_path, file_ref):
    with IndexTrackedFile(vit_repo_local_path) as index_tracked_file:
        file_data = index_tracked_file.get_files_data(vit_repo_local_path)
    if file_ref not in file_data:
        raise Asset_UntrackedFile_E(file_ref)
    package_path, asset_name, origin_file_name, editable, changes = file_data[file_ref]
    if not editable:
        raise Asset_NotEditable_E(file_ref)
    if not changes:
        raise Asset_NoChangeToCommit_E(file_ref)
    return package_path, asset_name, origin_file_name
