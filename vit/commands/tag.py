
def create_tag_light_from_branch(
        path, package_path,
        asset_name, branch, tagname):

    with ssh_connect_auto(path) as ssh_connection:

        tree_asset, tree_asset_path = fetch_tree.fetch_up_to_date_tree_asset(
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

        ssh_connection.put_auto(tree_asset_file_path, tree_asset_file_path)
