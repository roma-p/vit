import os
from vit import path_helpers
from vit.vit_lib.misc import (
    tree_fetch,
    file_name_generation,
    tree_func,
    package_func,
)
from vit.vit_lib.checkout_datatypes import (
    CheckoutType,
    Checkout
)
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.file_handlers.tree_asset import TreeAsset
from vit.file_handlers.index_tracked_file import IndexTrackedFile


def checkout_asset_by_branch(
        vit_connection, asset_path,
        branch, editable=False, rebase=False):
    checkout = Checkout(CheckoutType.branch, branch)
    return _checkout_asset(
        vit_connection, asset_path,
        checkout, editable, rebase
    )


def checkout_asset_by_commit(
        vit_connection, asset_path,
        commit_file_name, rebase=False):
    checkout = Checkout(CheckoutType.commit, commit_file_name)
    return _checkout_asset(
        vit_connection, asset_path,
        checkout, rebase=rebase
    )


def checkout_asset_by_tag(vit_connection, asset_path, tag, rebase=False):
    checkout = Checkout(CheckoutType.tag, tag)
    return _checkout_asset(
        vit_connection, asset_path,
        checkout, rebase=rebase
    )

# -----------------------------------------------------------------------------


def _checkout_asset(
        vit_connection,
        asset_path,
        checkout,
        editable=False,
        rebase=False):

    # 1. checks and gather infos.

    _, _, user = repo_config.get_origin_ssh_info(vit_connection.local_path)

    package_path, asset_name = package_func.split_asset_path(asset_path)

    staged_asset_tree = tree_fetch.fetch_up_to_date_stage_tree_asset(
        vit_connection, package_path, asset_name
    )

    with staged_asset_tree.file_handler as tree_asset:

        asset_origin_path, sha256 = _get_asset_origin_path(
            vit_connection, tree_asset,
            asset_name, checkout
        )

        if editable:
            tree_func.become_editor_of_asset(
                tree_asset, asset_name,
                asset_origin_path, user
            )


    asset_checkout_path = file_name_generation.generate_checkout_path(
        asset_origin_path,
        package_path,
        asset_name,
        _generate_suffix_from_checkout(checkout)
    )

    asset_checkout_path_local = path_helpers.localize_path(
        vit_connection.local_path,
        asset_checkout_path
    )

    package_local_path = path_helpers.localize_path(
        vit_connection.local_path,
        package_path
    )

    # 2. data transfer.

    if not os.path.exists(package_local_path):
        os.makedirs(package_local_path)

    if rebase or editable or not os.path.exists(asset_checkout_path_local):
        do_copy_origin_file = True
    else:
        do_copy_origin_file = False

    if do_copy_origin_file:
        vit_connection.get_data_from_origin(
            asset_origin_path,
            asset_checkout_path,
            is_editable=editable
        )

    # 3. update origin metadatas

    if editable:
        with vit_connection.lock_manager:
            vit_connection.update_staged_metadata(staged_asset_tree)
            with staged_asset_tree.file_handler as tree_asset:
                tree_func.become_editor_of_asset(
                    tree_asset, asset_name,
                    asset_origin_path, user
                )
            vit_connection.put_metadata_to_origin(staged_asset_tree)

    # 4. update local metadatas.

    with IndexTrackedFile(vit_connection.local_path) as index_tracked_file:
        index_tracked_file.add_tracked_file(
            package_path,
            asset_name,
            asset_checkout_path,
            checkout.checkout_type,
            checkout.checkout_value,
            origin_file_name=asset_origin_path,
            sha256=sha256
        )
    return asset_checkout_path


def _get_asset_origin_path(
        vit_connection, tree_asset,
        asset_name, checkout):
    func, exception = {
        CheckoutType.tag: (TreeAsset.get_tag, Tag_NotFound_E),
        CheckoutType.branch: (TreeAsset.get_branch_current_file, Branch_NotFound_E),
        CheckoutType.commit: (TreeAsset.get_commit, Commit_NotFound_E),
    }[checkout.checkout_type]


    asset_file_path = func(tree_asset, checkout.checkout_value)
    if asset_file_path is None:
        raise exception(asset_name, checkout.checkout_value)
    if checkout.checkout_type == CheckoutType.tag and isinstance(asset_file_path, dict):
        sha256 = asset_file_path.get("sha256")
        asset_file_path = asset_file_path.get("filepath")
    else: 
        sha256 = tree_asset.get_commit_sha256(asset_file_path)
    if not vit_connection.exists_on_origin(asset_file_path):
        raise Path_FileNotFoundAtOrigin_E(
            asset_file_path,
            vit_connection.ssh_link
        )
    return asset_file_path, sha256


def _generate_suffix_from_checkout(checkout):
    # FIXME: dirty hack... needs to separate asset_id from filename.
    if checkout.checkout_type == CheckoutType.commit:
        value_suffix = os.path.basename(checkout.checkout_value)
        value_suffix = os.path.splitext(value_suffix)[0]
        value_suffix = value_suffix.split("-")[-1]
    else:
        value_suffix = checkout.checkout_value
    return "{}-{}".format(checkout.checkout_type, value_suffix)
