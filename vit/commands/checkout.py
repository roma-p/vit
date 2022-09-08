
def checkout_asset_by_branch(local_path, package_path,
                             asset_name, branch,
                             editable=False,
                             rebase=False):

    _, _, user = repo_config.get_origin_ssh_info(path)

    with ssh_connect_auto(path) as ssh_connection:

        with fetch_up_to_date_tree_asset(
                ssh_connection, local_path,
                package_path, asset_name) as tree_asset:

            asset_origin_path = get_asset_file_path_by_branch(
                ssh_connection, tree_asset,
                asset_name, branch
            )

            if editable:
                vit_unit_of_work.become_editor_of_asset(
                    tree_asset, asset_name,
                    asset_origin_path, user
                )

            sha256 = tree_asset.get_sha256(asset_origin_path)

        if editable:
            ssh_connection.put_auto(tree_asset.path, tree_asset.path)

        asset_checkout_path = path_helpers.generate_checkout_path(
            asset_origin_path,
            package_path,
            asset_name,
            branch
        )   

        asset_checkout_path_local = path_helpers.localize_path(
            local_path,
            asset_path_raw
        )

        copy_origin_file = not os.path.exists(asset_checkout_path_local) or rebase

        vit_unit_of_work.fetch_asset_file(
            ssh_connection,
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
            origin_file_name=asset_origin_file_path,
            sha256=sha256
        )
    return asset_checkout_path

# -------------

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
