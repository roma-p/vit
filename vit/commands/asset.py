
def create_asset(
        path,
        package_path,
        asset_name,
        template_id):

    if not _check_is_vit_dir(path): return False

    _, _, user = repo_config.get_origin_ssh_info(path)

    with ssh_connect_auto(path) as ssh_connection:

        ssh_connection.get_vit_file(path, constants.VIT_PACKAGES)

        template_path, extension, sha256 = fetch_template_data(
            ssh_connection,
            path,
            template_id
        )

        asset_file_path = path_helpers.generate_unique_asset_file_path(
            package_path,
            asset_name,
            extension
        )

        tree_asset_file_path = path_helpers.generate_asset_tree_file_path(
            package_path,
            asset_name
        )

        tree_asset_file_path_local = path_helpers.localize_path(
            vit_repo_local_path,
            tree_asset_file_path
        )

        tree_package, tree_package_path = tree_fetch.fetch_up_to_date_tree_package(
            ssh_connection,
            local_path,
            package_path
        )
    
        with tree_package:
            if tree_package.get_asset_tree_file_path(asset_name) is not None:
                raise Asset_AlreadyExists_E(package_path, asset_name)
            tree_package.set_asset(asset_name, tree_asset_file_path)   

        tree_asset_file_dir_local = os.path.dirname(tree_asset_file_path_local)
        if not os.path.exists(tree_asset_file_dir_local):
            os.makedirs(tree_asset_file_dir_local)

        TreeAsset.create_file(tree_asset_file_path_local, asset_name)
        with TreeAsset(tree_asset_file_path_local) as tree_asset:
            tree_asset.add_commit(
                asset_file_path, None,
                time.time(), user,
                sha256, "asset created"
            )
            tree_asset.set_branch("base", asset_file_path)

            ssh_connection.put_auto(tree_package_path, tree_package_path)
        ssh_connection.put_auto(tree_asset_file_path_local, tree_asset_file_path_local)

        asset_origin_dir_path = path_helpers.get_asset_file_path_raw(
            package_path,
            asset_name
        )
        ssh_connection.mkdir(asset_origin_dir_path)
        ssh_connection.cp(template_path, asset_file_path)

        tree_asset_file_dir = os.path.dirname(tree_asset_file_path)
        ssh_connection.create_dir_if_not_exists(tree_asset_file_dir)
        ssh_connection.put_auto(tree_asset_file_path, tree_asset_file_path)
        ssh_connection.put_auto(tree_package_file_path, tree_package_file_path)

        ssh_connection.put_vit_file(path, constants.VIT_PACKAGES)


def release_editable(local_path, checkout_file):

    file_track_data = get_file_track_data(local_path, checkout_file)
    _, _, user = repo_config.get_origin_ssh_info(local_path)

    with ssh_connect_auto(local_path) as ssh_connection:

        tree_asset, tree_asset_path = fetch_tree.fetch_up_to_date_tree_asset(
                ssh_connection,
                local_path,
                file_track_data["package_path"],
                file_track_data["asset_name"]
        )

        with tree_asset:
            if tree_asset.get_editor(file_track_data["origin_file_name"]) != user:
                raise Asset_NotEditable_E(checkout_file)
            tree_asset.remove_editor(file_track_data["origin_file_name"])

        ssh_connection.put_auto(tree_asset_path, tree_asset_path)


# -----------------------------------------------------------------------------


def fetch_template_data(ssh_connection, local_path, template_id):
    ssh_connection.get_vit_file(local_path, constants.VIT_TEMPLATE_CONFIG)
    with IndexTemplate(local_path) as index_template:
        template_data = index_template.get_template_path_from_id(template_id)
    if not template_data:
        raise Template_NotFound_E(template_id)
    template_path, sha256 = template_data
    extension = py_helpers.get_file_extension(template_path)
    return template_path, extension, sha256


