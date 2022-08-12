import os
import uuid
import shutil
import time
import uuid

import logging
log = logging.getLogger()

from vit import py_helpers
from vit import constants

from vit import file_config
from vit import file_template
from vit import file_file_track_list
from vit.file_asset_tree_dir import AssetTreeFile

from vit.vit_connection import VitConnection, ssh_connect_auto
from vit.custom_exceptions import *

# INIT AND CLONING ------------------------------------------------------------

def init_origin(path):

    parent_dir = os.path.dirname(path)
    vit_dir = os.path.join(path, constants.VIT_DIR)
    vit_tmp_dir = os.path.join(path, constants.VIT_DIR, constants.VIT_TEMPLATE_DIR)

    if not os.path.exists(parent_dir):
        raise Path_ParentDirNotExist_E(path)
    if os.path.exists(path):
        raise Path_AlreadyExists_E(path)

    os.mkdir(path)
    os.mkdir(vit_dir)
    os.mkdir(vit_tmp_dir)

    file_config.create(path)
    file_template.create(path)
    file_file_track_list.create(path)


def clone(origin_link, clone_path, username, host="localhost"):

    parent_dir = os.path.dirname(clone_path)
    if not os.path.exists(parent_dir):
        raise Path_ParentDirNotExist_E(clone_path)
    if os.path.exists(clone_path):
        raise Path_AlreadyExists_E(clone_path)
    if host != "localhost":
        raise ValueError("only localhost is currently supported")

    os.mkdir(clone_path)
    vit_local_path  = os.path.join(clone_path, constants.VIT_DIR)
    vit_origin_path = os.path.join(origin_link, constants.VIT_DIR)

    with VitConnection(host, origin_link, username) as ssh_connection:
        if not ssh_connection.exists(vit_origin_path):
            raise OriginNotFound_E(ssh_connection.ssh_link)

        ssh_connection.get(
            os.path.join(origin_link, constants.VIT_DIR),
            vit_local_path,
            recursive=True
        )

    file_config.edit_on_clone(
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

        if not file_template.is_template_id_free(path, template_id):
            raise Template_AlreadyExists_E(template_id)

        template_scn_dst = os.path.join(
            constants.VIT_DIR,
            constants.VIT_TEMPLATE_DIR,
            os.path.basename(template_filepath)
        )

        file_template.reference_new_template(
            path,
            template_id,
            template_scn_dst,
            py_helpers.calculate_file_sha(template_filepath)
        )

        sshConnection.put_vit_file(path, constants.VIT_TEMPLATE_CONFIG)

        sshConnection.put(
            template_filepath,
            template_scn_dst
        )


def get_template_asset(path, template_id):
    pass

# CREATING NEW DATA -----------------------------------------------------------

def create_package(path, package_path, force_subtree=False):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:

        origin_package_dir = package_path
        origin_parent_dir = os.path.dirname(origin_package_dir)

        if sshConnection.exists(origin_package_dir):
            raise Path_AlreadyExists_E(origin_package_dir)

        if not sshConnection.exists(origin_parent_dir):
            if not force_subtree:
                raise Path_ParentDirNotExist_E(origin_parent_dir)
            sshConnection.mkdir(origin_parent_dir)

        sshConnection.mkdir(origin_package_dir)


def create_asset(
        path,
        package_path,
        asset_name,
        template_id):

    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:

        if not sshConnection.exists(package_path):
            raise Package_NotFound_E(package_path)

        asset_path = os.path.join(package_path, asset_name)
        if sshConnection.exists(asset_path):
            raise Path_AlreadyExists_E(asset_path)

        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)

        template_data = file_template.get_template_path_from_id(path, template_id)
        if not template_data:
            raise Template_NotFound_E(template_id)
        template_path, sha256 = template_data

        asset_path = os.path.join(package_path, asset_name)
        sshConnection.mkdir(asset_path)

        asset_file = _create_maya_filename(asset_name)
        sshConnection.cp(
            template_path,
            os.path.join(asset_path, asset_file)
        )

        _, _, user = file_config.get_origin_ssh_info(path)

        AssetTreeFile(
            path,package_path,
            asset_name).create_asset_tree_file(asset_file, user, sha256)

        sshConnection.create_tree_dir(package_path)
        sshConnection.put_tree_file(path, package_path, asset_name)


def fetch_asset_by_tag(
        path, package_path,
        asset_name, tag,
        rebase= False):

    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_tree_file(path, package_path, asset_name)

        with AssetTreeFile(path, package_path, asset_name) as treeFile:
            asset_filepath = treeFile.get_tag(tag)
            if asset_filepath is None: return False
            sha256 = treeFile.get_sha256(asset_filepath)

        asset_dir_local_path = os.path.join(path, package_path)
        asset_name_local = _format_asset_name_local(asset_name, tag)

        asset_local_path = os.path.join(
            asset_dir_local_path,
            asset_name_local
        )

        if not os.path.exists(asset_dir_local_path):
            os.makedirs(asset_dir_local_path)

        copy_origin_file = not os.path.exists(asset_local_path) or rebase
        if copy_origin_file:
            sshConnection.get(
                asset_filepath,
                asset_local_path
            )

    file_file_track_list.add_tracked_file(
        path, package_path,
        asset_name,
        os.path.join(
            package_path,
           asset_name_local),
        editable=False,
        origin_file_name=asset_filepath,
        sha256=sha256
    )

def fetch_asset_by_branch(
        path, package_path,
        asset_name, branch,
        editable=False,
        rebase=False):

    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_tree_file(path, package_path, asset_name)

        with AssetTreeFile(path, package_path, asset_name) as treeFile:
            asset_filepath = treeFile.get_branch_current_file(branch)
            if not asset_filepath:
                raise Branch_NotFound_E(asset_name, branch)
            if not sshConnection.exists(asset_filepath):
                raise Path_FileNotFoundAtOrigin_E(asset_filepath, sshConnection.ssh_link)

            if editable:
                editor = treeFile.get_editor(asset_filepath)
                if editor:
                    raise Asset_AlreadyEdited_E(asset_name, editor)
                _, _, user = file_config.get_origin_ssh_info(path)
                treeFile.set_editor(asset_filepath, user)
            sha256 = treeFile.get_sha256(asset_filepath)

        asset_dir_local_path = os.path.join(
            path, package_path
        )
        asset_name_local = _format_asset_name_local(asset_name, branch)

        asset_local_path = os.path.join(
            asset_dir_local_path,
            asset_name_local
        )

        if not os.path.exists(asset_dir_local_path):
            os.makedirs(asset_dir_local_path)

        copy_origin_file = not os.path.exists(asset_local_path) or rebase
        if copy_origin_file:
            sshConnection.get(
                asset_filepath,
                asset_local_path
            )
        sshConnection.put_tree_file(path, package_path, asset_name)

    file_file_track_list.add_tracked_file(
        path,
        package_path,
        asset_name,
        os.path.join(
            package_path,
            asset_name_local),
        editable=editable,
        origin_file_name=asset_filepath,
        sha256=sha256
    )
    return asset_local_path


def commit_file(path, filepath, keep=False):

    file_data = file_file_track_list.get_files_data(path)
    if filepath not in file_data:
        raise Asset_UntrackedFile_E(filepath)

    package_path, asset_name, origin_file_name, editable, changes = file_data[filepath]
    if not editable:
        raise Asset_NotEditable_E(filepath)
    if not changes:
        raise Asset_NoChangeToCommit_E(filepath)

    _, _, user = file_config.get_origin_ssh_info(path)
    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_tree_file(path, package_path, asset_name)
        # TODO: here, check if editor token has not been stolen...

        new_file_path = os.path.join(
            package_path,
            asset_name,
            _create_maya_filename(asset_name)
        )

        with AssetTreeFile(path, package_path, asset_name) as treeFile:

            if not treeFile.get_branch_from_file(origin_file_name):
                raise Asset_NotAtTipOfBranch(filepath, "TODO get branch...")

            treeFile.update_on_commit(
                filepath,
                new_file_path,
                origin_file_name,
                time.time(),
                user,
                keep
            )

        sshConnection.put(
            os.path.join(path, filepath),
            new_file_path
        )

        sshConnection.put_tree_file(path, package_path, asset_name)
        if not keep:
            os.remove(os.path.join(path, filepath))
            # TODO: another json that keep the file openned.
            file_file_track_list.remove_file(path, filepath)


def branch_from_origin_branch(
        path, package_path, asset_name,
        branch_parent, branch_new):

    _, _, user = file_config.get_origin_ssh_info(path)

    with ssh_connect_auto(path) as sshConnection:

        sshConnection.get_tree_file(path, package_path, asset_name)

        new_file_path = os.path.join(
            package_path,
            asset_name,
            _create_maya_filename(asset_name)
        )

        with AssetTreeFile(path, package_path, asset_name) as treeFile:

            branch_ref = treeFile.get_branch_current_file(branch_parent)
            if branch_ref is None:
                raise Branch_NotFound_E(asset_name, branch_parent)

            if treeFile.get_branch_current_file(branch_new):
                raise Branch_AlreadyExist_E(asset_name, branch_new)

            status = treeFile.create_new_branch_from_file(
                new_file_path,
                branch_parent,
                branch_new,
                time.time(),
                user
            )

        sshConnection.put_tree_file(path, package_path, asset_name)
        sshConnection.cp(branch_ref, new_file_path)


def clean(path):

    file_data = file_file_track_list.get_files_data(path)

    non_commited_files= []
    for data in file_data:
        if data[4]:
            non_commited_files.append(data)
    if non_commited_files:
        log.error("can't clean local repository, some changes needs to be commit")
        for (
                file_path,
                package_path,
                asset_name,
                editable,
                changes ) in non_commited_files:

            log.error("{}{} -> {} ".format(package_path,asset_name,
                                           file_path))
            return False
    for (file_path, _, _, _, _, _) in file_data:
        os.remove(os.path.join(path,
            file_path))
        return True

def create_tag_light_from_branch(path, package_path, asset_name, branch, tagname):

    with ssh_connect_auto(path) as sshConnection:

        sshConnection.get_tree_file(path, package_path, asset_name)

        with AssetTreeFile(path, package_path, asset_name) as treeFile:
            branch_ref = treeFile.get_branch_current_file(branch)
            if not branch_ref:
                raise Branch_NotFound_E(asset_name, branch)
            if treeFile.get_tag(tagname):
                raise Tag_AlreadyExists_E(asset_name, tagname)
            treeFile.add_tag_lightweight(branch_ref, tagname)

        sshConnection.put_tree_file(path, package_path, asset_name)

def get_status_local(path):
    return file_file_track_list.gen_status_local_data(path)

def _check_is_vit_dir(path):
    return os.path.exists(os.path.join(path, constants.VIT_DIR))

def _create_maya_filename(asset_name):
    return "{}-{}.ma".format(asset_name, uuid.uuid4())

def _format_asset_name_local(asset_name, branch):
    return "{}-{}.ma".format(asset_name, branch)

