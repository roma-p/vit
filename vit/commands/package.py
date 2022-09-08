
def create_package(path, package_path, force_subtree=False):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as ssh_connection:

        origin_package_dir = package_path
        origin_parent_dir = os.path.dirname(origin_package_dir)

        with IndexPackage(path) as package_index:
            if package_index.check_package_exists(package_path):
                raise Package_AlreadyExists_E(package_path)

            package_asset_file_name = path_helpers.generate_package_tree_file_name(
                package_path
            )
            package_asset_file_path = os.path.join(
                constants.VIT_DIR,
                constants.VIT_ASSET_TREE_DIR,
                package_asset_file_name
            )
            package_asset_file_local_path = path_helpers.localize_path(
                path,
                package_asset_file_path
            )

            if not ssh_connection.exists(origin_parent_dir):
                if not force_subtree:
                    raise Path_ParentDirNotExist_E(origin_parent_dir)

            package_index.set_package(package_path, package_asset_file_path)
            TreePackage.create_file(package_asset_file_local_path, package_path)
            ssh_connection.mkdir(origin_package_dir, p=True)

        ssh_connection.put_vit_file(path, constants.VIT_PACKAGES)
        ssh_connection.put_auto(
            package_asset_file_path,
            package_asset_file_path,
            recursive=True
        )
