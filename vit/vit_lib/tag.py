import time
from vit import py_helpers
from vit.connection.vit_connection import ssh_connect_auto
from vit.vit_lib.misc import (
    tree_fetch,
    file_name_generation,
    tag_versionned_func
)
from vit.file_handlers import repo_config
from vit.vit_lib.misc.tree_asset_repo import TreeAssetRepo
from vit.custom_exceptions import *

def create_tag_light_from_branch(
        local_path, package_path,
        asset_name, branch, tagname):

    if tag_versionned_func.check_is_auto_tag(tagname):
        raise Tag_NameMatchVersionnedTag_E(tagname)

    with TreeAssetRepo(local_path, package_path, asset_name) as treeAssetRepo:

        branch_ref = treeAssetRepo.tree_asset.get_branch_current_file(branch)
        if not branch_ref:
            raise Branch_NotFound_E(asset_name, branch)
        if treeAssetRepo.tree_asset.get_tag(tagname):
            raise Tag_AlreadyExists_E(asset_name, tagname)
        treeAssetRepo.tree_asset.add_tag_lightweight(branch_ref, tagname)


def create_tag_annotated_from_branch(
        local_path, package_path,
        asset_name, branch,
        tag_name, message):

    if tag_versionned_func.check_is_auto_tag(tag_name):
        raise Tag_NameMatchVersionnedTag_E(tag_name)

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with TreeAssetRepo(local_path, package_path, asset_name) as treeAssetRepo:

        asset_parent_path = get_asset_branch_file(treeAssetRepo.tree_asset, asset_name, branch)

        new_file_path = file_name_generation.generate_unique_asset_file_path(
            package_path,
            asset_name,
            py_helpers.get_file_extension(asset_parent_path)
        )

        treeAssetRepo.tree_asset.add_tag_annotated(
            asset_parent_path,
            new_file_path,
            tag_name, time.time(),
            user, message
        )
        treeAssetRepo.ssh_connection.cp(asset_parent_path, new_file_path)


def list_tags(local_path, package_path, asset_name):
    with ssh_connect_auto(local_path) as ssh_connection:
        tree_asset, _ = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )
        with tree_asset:
            tags = tree_asset.list_tags()
    return tags


def list_auto_tags_by_branch(local_path, package_path, asset_name, branch):
    tags = list_tags(local_path, package_path, asset_name)
    return tuple([
        t for t in list_tags(local_path, package_path, asset_name)
        if tag_versionned_func.check_is_auto_tag_of_branch(asset_name, branch, t)
    ])


def create_tag_auto_from_branch(
        local_path, package_path,
        asset_name, branch,
        message, update_idx):

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with TreeAssetRepo(local_path, package_path, asset_name) as treeAssetRepo:

        previous_auto_tag = treeAssetRepo.tree_asset.get_last_auto_tag(branch)
        if previous_auto_tag:
            version_numbers = list(
                tag_versionned_func.get_version_from_tag_auto(
                    previous_auto_tag
                )
            )
        else:
            version_numbers = [0, 0, 0]

        version_numbers = tag_versionned_func.increment_version(
            update_idx,
            *version_numbers
        )

        tag_name = tag_versionned_func.generate_tag_auto_name_by_branch(
            asset_name,
            branch,
            *version_numbers
        )
        treeAssetRepo.tree_asset.set_last_auto_tag(branch, tag_name)

        asset_parent_path = get_asset_branch_file(treeAssetRepo.tree_asset, asset_name, branch)

        new_file_path = file_name_generation.generate_unique_asset_file_path(
            package_path,
            asset_name,
            py_helpers.get_file_extension(asset_parent_path)
        )

        treeAssetRepo.tree_asset.add_tag_annotated(
            asset_parent_path,
            new_file_path,
            tag_name, time.time(),
            user, message
        )
        treeAssetRepo.ssh_connection.cp(asset_parent_path, new_file_path)

# ----------------------------------------------------------------------------

def get_asset_branch_file(tree_asset, asset_name,  branch):
    asset_file_path =  tree_asset.get_branch_current_file(branch)
    if not asset_file_path:
        raise Branch_NotFound_E(asset_name, branch)
    return asset_file_path
