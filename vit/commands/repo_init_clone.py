def init_origin(path):

    parent_dir = os.path.dirname(path)
    vit_dir = os.path.join(path, constants.VIT_DIR)
    vit_tmp_dir = os.path.join(path, constants.VIT_DIR, constants.VIT_TEMPLATE_DIR)
    vit_tree_dir = os.path.join(path, constants.VIT_DIR, constants.VIT_ASSET_TREE_DIR)

    if not os.path.exists(parent_dir):
        raise Path_ParentDirNotExist_E(path)
    if os.path.exists(path):
        raise Path_AlreadyExists_E(path)

    os.mkdir(path)
    os.mkdir(vit_dir)
    os.mkdir(vit_tmp_dir)
    os.mkdir(vit_tree_dir)

    repo_config.create(path)

    IndexTemplate.create_file(path)
    IndexTrackedFile.create_file(path)
    IndexPackage.create_file(path)


def clone(origin_link, clone_path, username, host="localhost"):

    parent_dir = os.path.dirname(clone_path)
    if not os.path.exists(parent_dir):
        raise Path_ParentDirNotExist_E(clone_path)
    if os.path.exists(clone_path):
        raise Path_AlreadyExists_E(clone_path)
    if host != "localhost":
        raise ValueError("only localhost is currently supported")

    vit_local_path = os.path.join(clone_path, constants.VIT_DIR)
    vit_origin_path = os.path.join(origin_link, constants.VIT_DIR)

    with VitConnection(clone_path, host, origin_link, username) as ssh_connection:

        if not ssh_connection.exists(constants.VIT_DIR):
            raise OriginNotFound_E(ssh_connection.ssh_link)

        os.mkdir(clone_path)

        ssh_connection.get(
            constants.VIT_DIR,
            vit_local_path,
            recursive=True
        )

    repo_config.edit_on_clone(
        clone_path,
        host,
        origin_link,
        username
    