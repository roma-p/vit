from vit.connection.vit_connection import ssh_connect_auto
from vit.vit_lib.misc import tree_fetch
from vit.custom_exceptions import *

def create_tag_light_from_branch(
        local_path, package_path,
        asset_name, branch, tagname):

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )

        with tree_asset:
            branch_ref = tree_asset.get_branch_current_file(branch)
            if not branch_ref:
                raise Branch_NotFound_E(asset_name, branch)
            if tree_asset.get_tag(tagname):
                raise Tag_AlreadyExists_E(asset_name, tagname)
            tree_asset.add_tag_lightweight(branch_ref, tagname)

        ssh_connection.put_auto(tree_asset_path, tree_asset_path)

def list_tags(local_path, package_path, asset_name):
    with ssh_connect_auto(local_path) as ssh_connection:
        tree_asset, _ = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )
        with tree_asset:
            tags = tree_asset.list_tags()
    return tags

