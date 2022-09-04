import time
from vit import path_helpers
from vit import py_helpers
from vit import constants
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.index_template import IndexTemplate
from vit.file_handlers.tree_package import TreePackage
from vit.file_handlers.tree_asset import TreeAsset
from vit.file_handlers.index_tracked_file import IndexTrackedFile
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
        raise Package_NotFound_E(package_path)

    ssh_connection.get(
        package_file_name,
        path_helpers.localize_path(path, package_file_name)
    )

    with TreePackage(os.path.join(path, package_file_name)) as tree_package:
        asset_file_tree_path = tree_package.get_asset_tree_file_path(asset_name)
    if not asset_file_tree_path:
        raise Asset_NotFound_E(package_path, asset_name)
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

# ----


def get_template_data(vit_repo_local_path, template_id):
    # FIXME ? maybe fetch? 
    with IndexTemplate(vit_repo_local_path) as index_template:
        template_data = index_template.get_template_path_from_id(template_id)
    if not template_data:
        raise Template_NotFound_E(template_id)
    template_path, sha256 = template_data
    extension = py_helpers.get_file_extension(template_path)
    return template_path, extension, sha256

# ----


def get_package_tree_path(vit_repo_local_path, package_path):
    with IndexPackage(vit_repo_local_path) as package_index:
        tree_package_file_path = package_index.get_package_tree_file_path(package_path)
    if not tree_package_file_path:
        raise Package_NotFound_E(package_path)
    return tree_package_file_path

# ----


def reference_new_asset_in_tree(
        vit_repo_local_path,
        tree_package_file_path,
        tree_asset_file_path,
        package_path,
        asset_name,
        asset_file_path,
        user, sha256,
        commit_mess):

    package_tree_file_path_local = path_helpers.localize_path(
        vit_repo_local_path,
        tree_package_file_path
    )
    tree_asset_file_path_local = path_helpers.localize_path(
        vit_repo_local_path,
        tree_asset_file_path
    )
    tree_asset_file_dir_local = os.path.dirname(tree_asset_file_path_local)

    with TreePackage(package_tree_file_path_local) as tree_package:
        if tree_package.get_asset_tree_file_path(asset_name) is not None:
            raise Asset_AlreadyExists_E(package_path, asset_name)
        tree_package.set_asset(asset_name, tree_asset_file_path)

    if not os.path.exists(tree_asset_file_dir_local):
        os.makedirs(tree_asset_file_dir_local)

    TreeAsset.create_file(tree_asset_file_path_local, asset_name)
    with TreeAsset(tree_asset_file_path_local) as tree_asset:
        tree_asset.add_commit(asset_file_path, None, time.time(), user, sha256, commit_mess)
        tree_asset.set_branch("base", asset_file_path)

# ----


def fetch_asset_file(
        ssh_connection,
        origin_file_path,
        local_file_path,
        do_copy=False):
    package_path_local = os.path.dirname(local_file_path)
    if not os.path.exists(package_path_local):
        os.makedirs(package_path_local)
    if do_copy:
        ssh_connection.get(origin_file_path, local_file_path)
