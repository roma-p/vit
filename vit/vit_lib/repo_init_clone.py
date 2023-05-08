import os
from vit import constants

from vit.custom_exceptions import *
from vit.file_handlers import repo_config
from vit.path_helpers import localize_path
from vit.file_handlers.index_package import IndexPackage
from vit.file_handlers.index_template import IndexTemplate
from vit.file_handlers.index_tracked_file import IndexTrackedFile


def init_origin(path):

    parent_dir = os.path.dirname(path)
    vit_dir = localize_path(path, constants.VIT_DIR)
    vit_tmp_dir = localize_path(path, constants.VIT_TEMPLATE_DIR)
    vit_tree_dir = localize_path(path, constants.VIT_ASSET_TREE_DIR)
    vit_stage_dir = localize_path(path, constants.VIT_STAGE_DIR)

    if not os.path.exists(parent_dir):
        raise Path_ParentDirNotExist_E(path)
    if os.path.exists(path):
        raise Path_AlreadyExists_E(path)

    os.mkdir(path)
    os.mkdir(vit_dir)
    os.mkdir(vit_tmp_dir)
    os.mkdir(vit_tree_dir)
    os.mkdir(vit_stage_dir)

    repo_config.RepoConfig.create(path)

    IndexTrackedFile.create_file(path)
    IndexPackage.create_file(localize_path(path, constants.VIT_PACKAGES))
    IndexTemplate.create_file(localize_path(path, constants.VIT_TEMPLATE_CONFIG))


def clone(vit_connection, origin_link, clone_path, user, host="localhost"):

    parent_dir = os.path.dirname(clone_path)
    if not os.path.exists(parent_dir):
        raise Path_ParentDirNotExist_E(clone_path)
    if os.path.exists(clone_path):
        raise Path_AlreadyExists_E(clone_path)
    if host != "localhost":
        raise ValueError("only localhost is currently supported")

    vit_local_path = os.path.join(clone_path, constants.VIT_DIR)

    if not vit_connection.exists(constants.VIT_DIR):
        raise OriginNotFound_E(vit_connection.ssh_link)

    os.mkdir(clone_path)

    vit_connection.get_metadata_from_origin(constants.VIT_DIR, recursive=True)

    with repo_config.RepoConfig(clone_path) as rep:
        rep.edit_on_clone(host, origin_link, user)
