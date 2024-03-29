import os
from vit import path_helpers
from vit.vit_lib.misc import (
    tree_fetch,
    file_name_generation,
    tree_func
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
        local_path, vit_connection,
        package_path, asset_name, branch,
        editable=False,
        rebase=False):
    checkout = Checkout(CheckoutType.branch, branch)
    return _checkout_asset(
        local_path, vit_connection,
        package_path, asset_name,
        checkout, editable, rebase
    )


def checkout_asset_by_commit(
        local_path, vit_connection,
        package_path, asset_name,
        commit_file_name,
        rebase=False):
    checkout = Checkout(CheckoutType.commit, commit_file_name)
    return _checkout_asset(
        local_path, vit_connection,
        package_path, asset_name,
        checkout, rebase=rebase
    )


def checkout_asset_by_tag(
        local_path, vit_connection,
        package_path, asset_name,
        tag, rebase=False):
    checkout = Checkout(CheckoutType.tag, tag)
    return _checkout_asset(
        local_path, vit_connection,
        package_path, asset_name,
        checkout, rebase=rebase
    )

# -----------------------------------------------------------------------------


def _checkout_asset(
        local_path, vit_connection,
        package_path, asset_name,
        checkout,
        editable=False,
        rebase=False):

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
        vit_connection, local_path,
        package_path, asset_name
    )

    with tree_asset:

        asset_origin_path = _get_asset_origin_path(
            vit_connection, tree_asset,
            asset_name, checkout
        )

        if editable:
            tree_func.become_editor_of_asset(
                tree_asset, asset_name,
                asset_origin_path, user
            )

        sha256 = tree_asset.get_sha256(asset_origin_path)

    if editable:
        vit_connection.put_auto(tree_asset_path, tree_asset_path)

    asset_checkout_path = file_name_generation.generate_checkout_path(
        asset_origin_path,
        package_path,
        asset_name,
        _generate_suffix_from_checkout(checkout)
    )

    asset_checkout_path_local = path_helpers.localize_path(
        local_path,
        asset_checkout_path
    )

    copy_origin_file = not os.path.exists(asset_checkout_path_local) or rebase

    vit_connection.fetch_asset_file(
        asset_origin_path,
        asset_checkout_path_local,
        copy_origin_file
    )

    with IndexTrackedFile(local_path) as index_tracked_file:
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
    if not asset_file_path:
        raise exception(asset_name, checkout.checkout_value)
    if not vit_connection.exists(asset_file_path):
        raise Path_FileNotFoundAtOrigin_E(
            asset_file_path,
            vit_connection.ssh_link
        )
    return asset_file_path


def _generate_suffix_from_checkout(checkout):
    # FIXME: dirty hack... needs to separate asset_id from filename.
    if checkout.checkout_type == CheckoutType.commit:
        value_suffix = os.path.basename(checkout.checkout_value)
        value_suffix = os.path.splitext(value_suffix)[0]
        value_suffix = value_suffix.split("-")[-1]
    else:
        value_suffix = checkout.checkout_value
    return "{}-{}".format(checkout.checkout_type, value_suffix)
