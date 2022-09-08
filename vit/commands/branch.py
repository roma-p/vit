def branch_from_origin_branch(
        path, package_path, asset_name,
        branch_parent, branch_new):

    _, _, user = repo_config.get_origin_ssh_info(path)

    with ssh_connect_auto(path) as ssh_connection:

        tree_asset, tree_asset_path = fetch_tree.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )

        with tree_asset:

            branch_ref = tree_asset.get_branch_current_file(branch_parent)
            if branch_ref is None:
                raise Branch_NotFound_E(asset_name, branch_parent)

            if tree_asset.get_branch_current_file(branch_new):
                raise Branch_AlreadyExist_E(asset_name, branch_new)

            extension = py_helpers.get_file_extension(branch_ref)
            new_file_path = path_helpers.generate_unique_asset_file_path(
                package_path,
                asset_name,
                extension
            )

            tree_asset.create_new_branch_from_file(
                new_file_path,
                branch_parent,
                branch_new,
                time.time(),
                user
            )

        ssh_connection.put_auto(tree_asset_file_path, tree_asset_file_path)
        ssh_connection.cp(branch_ref, new_file_path)
