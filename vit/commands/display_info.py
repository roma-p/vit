def list_templates(path):
    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)
        with IndexTemplate(path) as index_template:
            template_data = index_template.get_template_data()
    return template_data


def list_packages(path):
    if not _check_is_vit_dir(path): return False
    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_vit_file(path, constants.VIT_PACKAGES)
        with IndexPackage(path) as package_index:
            ret = package_index.list_packages()
    return ret


def list_assets(path, package_path):
    if not _check_is_vit_dir(path): return False
    with ssh_connect_auto(path) as sshConnection:
        tree_dir = os.path.join(
            constants.VIT_DIR,
            constants.VIT_ASSET_TREE_DIR
        )
        sshConnection.get(
            tree_dir,
            os.path.join(path, tree_dir),
            recursive=True
        )
        with IndexPackage(path) as package_index:
            package_tree_path = package_index.get_package_tree_file_path(
                package_path
                )
        if not package_tree_path:
            raise Package_NotFound_E(package_path)

        with TreePackage(
                path_helpers.localize_path(
                    path,
                    package_tree_path)) as tree_package:
            ret = tree_package.list_assets()
    return ret


def list_branches(path, package_path, asset_name):
    if not _check_is_vit_dir(path): return False
    with ssh_connect_auto(path) as ssh_connection:
        tree_asset_file_path = vit_unit_of_work.fetch_asset_file_tree(
            ssh_connection, path,
            package_path, asset_name
        )
        with TreeAsset(
                path_helpers.localize_path(
                    path,
                    tree_asset_file_path)) as tree_asset:
            branches = tree_asset.list_branches()
    return branches


def list_tags(path, package_path, asset_name):
    if not _check_is_vit_dir(path): return False
    with ssh_connect_auto(path) as ssh_connection:
        tree_asset_file_path = vit_unit_of_work.fetch_asset_file_tree(
            ssh_connection, path,
            package_path, asset_name
        )
        with TreeAsset(
                path_helpers.localize_path(
                    path,
                    tree_asset_file_path)) as tree_asset:
            tags = tree_asset.list_tags()
    return tagss

def get_info_from_ref_file(path, ref_file):
    ref_file_local = path_helpers.localize_path(path, ref_file)
    if not os.path.exists(ref_file_local):
        raise Path_FileNotFound_E(ref_file_local)
    with IndexTrackedFile(path) as index_tracked_file:
        file_data = index_tracked_file.get_files_data(path)
    if ref_file not in file_data:
        raise Asset_UntrackedFile_E(ref_file)
    return file_data[ref_file]
    # TODO editable information not here... Needs refacto.
