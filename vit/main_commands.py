import time

from vit import py_helpers
from vit import path_helpers
from vit import constants

from vit import vit_unit_of_work

from vit.file_handlers import repo_config
from vit.file_handlers.index_template import IndexTemplate
from vit.file_handlers.index_tracked_file import IndexTrackedFile
from vit.file_handlers.index_package import IndexPackage

from vit.file_handlers.tree_package import TreePackage
from vit.file_handlers.tree_asset import TreeAsset

from vit.connection.vit_connection import VitConnection, ssh_connect_auto
from vit.custom_exceptions import *

import logging
log = logging.getLogger()

# INIT AND CLONING ------------------------------------------------------------


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
    )

# CONFIGURING REPO ------------------------------------------------------------


def create_template_asset(path, template_id, template_filepath, force=False):
    if not os.path.exists(template_filepath):
        raise Path_FileNotFound_E(template_filepath)

    with ssh_connect_auto(path) as sshConnection:

        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)

        with IndexTemplate(path) as index_template:

            if not force and not index_template.is_template_id_free(template_id):
                raise Template_AlreadyExists_E(template_id)

            template_scn_dst = os.path.join(
                constants.VIT_DIR,
                constants.VIT_TEMPLATE_DIR,
                os.path.basename(template_filepath)
            )

            index_template.reference_new_template(
                template_id,
                template_scn_dst,
                py_helpers.calculate_file_sha(template_filepath)
            )

        sshConnection.put_vit_file(path, constants.VIT_TEMPLATE_CONFIG)

        sshConnection.put(
            template_filepath,
            template_scn_dst
        )


def get_template(path, template_id):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:

        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)

        with IndexTemplate(path) as index_template:
            template_data = index_template.get_template_path_from_id(template_id)
            if not template_data:
                raise Template_NotFound_E(template_id)

        template_path_origin, sha256 = template_data
        template_path_local = os.path.join(path, os.path.basename(template_path_origin))

        sshConnection.get(
            template_path_origin,
            template_path_local
        )
    return template_path_local

# CREATING NEW DATA -----------------------------------------------------------


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


def create_asset(
        path,
        package_path,
        asset_name,
        template_id):

    if not _check_is_vit_dir(path): return False

    _, _, user = repo_config.get_origin_ssh_info(path)

    with ssh_connect_auto(path) as ssh_connection:

        ssh_connection.get_vit_file(path, constants.VIT_PACKAGES)

        template_path, extension, sha256 = vit_unit_of_work.get_template_data(
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

        tree_package_file_path = vit_unit_of_work.get_package_tree_path(
            path,
            package_path
        )

        vit_unit_of_work.reference_new_asset_in_tree(
            path,
            tree_package_file_path,
            tree_asset_file_path,
            package_path,
            asset_name,
            asset_file_path,
            user, sha256,
            "asset created")

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


def branch_from_origin_branch(
        path, package_path, asset_name,
        branch_parent, branch_new):

    _, _, user = repo_config.get_origin_ssh_info(path)

    with ssh_connect_auto(path) as ssh_connection:

        tree_asset_file_path = vit_unit_of_work.fetch_asset_file_tree(
            ssh_connection, path,
            package_path, asset_name
        )

        with TreeAsset(
            path_helpers.localize_path(
                path,
                tree_asset_file_path)) as tree_asset:

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


def create_tag_light_from_branch(
        path, package_path,
        asset_name, branch, tagname):

    with ssh_connect_auto(path) as ssh_connection:

        tree_asset_file_path = vit_unit_of_work.fetch_asset_file_tree(
            ssh_connection, path,
            package_path, asset_name
        )

        with TreeAsset(
                path_helpers.localize_path(
                    path,
                    tree_asset_file_path)) as tree_asset:

            branch_ref = tree_asset.get_branch_current_file(branch)
            if not branch_ref:
                raise Branch_NotFound_E(asset_name, branch)
            if tree_asset.get_tag(tagname):
                raise Tag_AlreadyExists_E(asset_name, tagname)
            tree_asset.add_tag_lightweight(branch_ref, tagname)

        ssh_connection.put_auto(tree_asset_file_path, tree_asset_file_path)


def get_status_local(path):
    with IndexTrackedFile(path) as index_tracked_file:
        data = index_tracked_file.gen_status_local_data(path)
    return data


def _check_is_vit_dir(path):
    return os.path.exists(os.path.join(path, constants.VIT_DIR))

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

# LISTING DATA ---------------------------------------------------------------


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
    return tags
