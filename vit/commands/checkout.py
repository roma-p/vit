from vit import path_helpers
from vit import tree_fetch
from vit import file_name_generation
from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.file_handlers.index_tracked_file import IndexTrackedFile


def checkout_asset_by_branch(local_path, package_path,
                             asset_name, branch,
                             editable=False,
                             rebase=False):

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )

        with tree_asset:

            asset_origin_path = get_asset_file_path_by_branch(
                ssh_connection, tree_asset,
                asset_name, branch
            )

            if editable:
                become_editor_of_asset(
                    tree_asset, asset_name,
                    asset_origin_path, user
                )

            sha256 = tree_asset.get_sha256(asset_origin_path)

        if editable:
            ssh_connection.put_auto(tree_asset_path, tree_asset_path)

        asset_checkout_path = file_name_generation.generate_checkout_path(
            asset_origin_path,
            package_path,
            asset_name,
            branch
        )

        asset_checkout_path_local = path_helpers.localize_path(
            local_path,
            asset_checkout_path
        )

        copy_origin_file = not os.path.exists(asset_checkout_path_local) or rebase

        ssh_connection.fetch_asset_file(
            asset_origin_path,
            asset_checkout_path_local,
            copy_origin_file
        )

    with IndexTrackedFile(local_path) as index_tracked_file:
        index_tracked_file.add_tracked_file(
            package_path,
            asset_name,
            asset_checkout_path,
            "branch", branch,
            origin_file_name=asset_origin_path,
            sha256=sha256
        )
    return path_helpers.localize_path(local_path, asset_checkout_path)


def checkout_asset_by_tag(
        local_path,
        package_path,
        asset_name, tag,
        rebase=False):

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )

        with tree_asset:

            asset_origin_file_path = tree_asset.get_tag(tag)
            # FIXME: raise error.
            if asset_origin_file_path is None:
                return

            sha256 = tree_asset.get_sha256(asset_origin_file_path)

        asset_checkout_path = file_name_generation.generate_checkout_path(
            asset_origin_file_path,
            package_path,
            asset_name,
            tag
        )
        asset_path_local = path_helpers.localize_path(
            local_path,
            asset_checkout_path
        )

        copy_origin_file = not os.path.exists(asset_path_local) or rebase

        ssh_connection.fetch_asset_file(
            ssh_connection,
            asset_origin_file_path,
            asset_path_local,
            copy_origin_file
        )

        ssh_connection.put_auto(tree_asset_path, tree_asset_path)

    with IndexTrackedFile(local_path) as index_tracked_file:
        index_tracked_file.add_tracked_file(
            package_path,
            asset_name,
            asset_checkout_path,
            "tag", tag,
            origin_file_name=asset_origin_file_path,
            sha256=sha256
        )

# -----------------------------------------------------------------------------

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

def become_editor_of_asset(tree_asset, asset_name, asset_filepath, user):
    editor = tree_asset.get_editor(asset_filepath)
    if editor:
        raise Asset_AlreadyEdited_E(asset_name, editor)
    tree_asset.set_editor(asset_filepath, user)
