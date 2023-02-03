import os
from vit import constants

from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.index_template import IndexTemplate
from vit.file_handlers.index_tracked_file import IndexTrackedFile


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

    repo_config.RepoConfig.create(path)

    IndexTemplate.create_file(path)
    IndexTrackedFile.create_file(path)
    IndexPackage.create_file(path)


def clone(origin_link, clone_path, user, host="localhost"):

    parent_dir = os.path.dirname(clone_path)
    if not os.path.exists(parent_dir):
        raise Path_ParentDirNotExist_E(clone_path)
    if os.path.exists(clone_path):
        raise Path_AlreadyExists_E(clone_path)
    if host != "localhost":
        raise ValueError("only localhost is currently supported")

    vit_local_path = os.path.join(clone_path, constants.VIT_DIR)

    with VitConnection(clone_path, host, origin_link, user) as ssh_connection:

        if not ssh_connection.exists(constants.VIT_DIR):
            raise OriginNotFound_E(ssh_connection.ssh_link)

        os.mkdir(clone_path)

        ssh_connection.get(
            constants.VIT_DIR,
            vit_local_path,
            recursive=True
        )
    with repo_config.RepoConfig(clone_path) as rep:
        rep.edit_on_clone(host, origin_link, user)
