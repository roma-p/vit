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

