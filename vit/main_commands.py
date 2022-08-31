import os
import glob
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
from vit.file_template import FileTemplate
from vit.file_file_track_list import FileTracker
from vit.file_asset_tree_dir import AssetTreeFile

from vit.file_packages import PackageIndex
from vit.file_package_tree import FilePackageTree

from vit.vit_connection import VitConnection, ssh_connect_auto
from vit.custom_exceptions import *

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

    file_config.create(path)
    FileTemplate.create_file(path)
    FileTracker.create_file(path)

    PackageIndex.create_file(path)


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

        with FileTemplate(path) as file_template:

            if not force and not file_template.is_template_id_free(template_id):
                raise Template_AlreadyExists_E(template_id)

            template_scn_dst = os.path.join(
                constants.VIT_DIR,
                constants.VIT_TEMPLATE_DIR,
                os.path.basename(template_filepath)
            )

            file_template.reference_new_template(
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

        with FileTemplate(path) as file_template:
            template_data = file_template.get_template_path_from_id(template_id)
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

    with ssh_connect_auto(path) as sshConnection:

        origin_package_dir = package_path
        origin_parent_dir = os.path.dirname(origin_package_dir)

        with PackageIndex(path) as package_index:
            if package_index.check_package_exists(package_path):
                raise Package_AlreadyExists_E(package_path)

            package_asset_file_name = _format_package_tree_file_name(package_path)
            package_asset_file_path = os.path.join(
                constants.VIT_DIR,
                constants.VIT_ASSET_TREE_DIR,
                package_asset_file_name
            )
            package_asset_file_local_path = os.path.join(path, package_asset_file_path)

            if not sshConnection.exists(origin_parent_dir):
                if not force_subtree:
                    raise Path_ParentDirNotExist_E(origin_parent_dir)

            package_index.set_package(package_path, package_asset_file_path)
            FilePackageTree.create_file(package_asset_file_local_path, package_path)
            sshConnection.mkdir(origin_package_dir, p=True)

    sshConnection.put_vit_file(path, constants.VIT_PACKAGES)
    sshConnection.put(package_asset_file_local_path, package_asset_file_path, recursive=True)

def create_asset(
        path,
        package_path,
        asset_name,
        template_id):

    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:

        sshConnection.get_vit_file(path, constants.VIT_PACKAGES)

        asset_path = os.path.join(package_path, asset_name)
        sshConnection.mkdir(asset_path)
        asset_file = _create_maya_filename(asset_name)
        _, _, user = file_config.get_origin_ssh_info(path)

        asset_tree_file_path = get_asset_file_tree_path(package_path, asset_name)
        asset_tree_file_dir  = os.path.dirname(asset_tree_file_path)

        with FileTemplate(path) as file_template:
            template_data = file_template.get_template_path_from_id(template_id)
        if not template_data:
            raise Template_NotFound_E(template_id)
        template_path, sha256 = template_data

        with PackageIndex(path) as package_index:
            package_file_name = package_index.get_package_tree_file_path(package_path)
        if not package_file_name:
            raise Package_NotFound_E(package_path)

        with FilePackageTree(os.path.join(path, package_file_name)) as package_tree:
            asset_file_tree_path = package_tree.get_asset_tree_file_path(asset_name)
            if asset_file_tree_path is not None:
                raise Asset_AlreadyExists_E(package_path, asset_name)
            package_tree.set_asset(asset_name, asset_tree_file_path)

        sshConnection.cp(
            template_path,
            os.path.join(asset_path, asset_file)
        )

        asset_tree_file_path_local = os.path.join(path, asset_tree_file_path)
        asset_tree_file_dir_local  = os.path.dirname(asset_tree_file_path_local)

        if not os.path.exists(asset_tree_file_dir_local):
            os.makedirs(asset_tree_file_dir_local)
        AssetTreeFile.create_file(asset_tree_file_path_local, asset_name)
        with AssetTreeFile(asset_tree_file_path_local) as asset_tree_file:
            asset_tree_file.add_commit(
                os.path.join(asset_path, asset_file),
                None, time.time(), user, sha256
            )
            asset_tree_file.set_branch("base", os.path.join(asset_path, asset_file))

        sshConnection.create_dir_if_not_exists(asset_tree_file_dir)
        sshConnection.put(
            asset_tree_file_path_local,
            asset_tree_file_path
        )
        sshConnection.put(
            os.path.join(path, package_file_name),
            package_file_name
        )
        sshConnection.put_vit_file(path, constants.VIT_PACKAGES)

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

    with FileTracker(path) as file_tracker:
        
        file_tracker.add_tracked_file(
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

        asset_tree_file_path = get_asset_file_tree(sshConnection, path, package_path, asset_name)
        asset_tree_file_path_local = os.path.join(path, asset_tree_file_path)

        with AssetTreeFile(asset_tree_file_path_local) as treeFile:

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
        sshConnection.put(asset_tree_file_path_local, asset_tree_file_path)

    with FileTracker(path) as file_tracker:
        file_tracker.add_tracked_file(
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

    with FileTracker(path) as file_tracker:
        file_data = file_tracker.get_files_data(path)
    if filepath not in file_data:
        raise Asset_UntrackedFile_E(filepath)

    package_path, asset_name, origin_file_name, editable, changes = file_data[filepath]
    if not editable:
        raise Asset_NotEditable_E(filepath)
    if not changes:
        raise Asset_NoChangeToCommit_E(filepath)

    _, _, user = file_config.get_origin_ssh_info(path)
    with ssh_connect_auto(path) as sshConnection:
        asset_tree_file_path = get_asset_file_tree(sshConnection, path, package_path, asset_name)
        asset_tree_file_path_local = os.path.join(path, asset_tree_file_path)

        new_file_path = os.path.join(
            package_path,
            asset_name,
            _create_maya_filename(asset_name)
        )

        with AssetTreeFile(asset_tree_file_path_local) as treeFile:

            if not treeFile.get_branch_from_file(origin_file_name):
                raise Asset_NotAtTipOfBranch(filepath, "TODO get branch...")

            treeFile.update_on_commit(
                os.path.join(path, filepath),
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

        sshConnection.put(asset_tree_file_path_local, asset_tree_file_path)
        if not keep:
            os.remove(os.path.join(path, filepath))
            with FileTracker(path) as file_tracker:
                file_tracker.remove_file(filepath)

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

    with FileTracker(path) as file_tracker:
        file_data = file_tracker.get_files_data(path)

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
    with FileTracker(path) as file_tracker:
        data = file_tracker.gen_status_local_data(path)
    return data

def _check_is_vit_dir(path):
    return os.path.exists(os.path.join(path, constants.VIT_DIR))

def _create_maya_filename(asset_name):
    return "{}-{}.ma".format(asset_name, uuid.uuid4())

def _format_asset_name_local(asset_name, branch):
    return "{}-{}.ma".format(asset_name, branch)

def _format_package_tree_file_name(package_path):
    return package_path.replace("/", "-")+".json"

def _format_asset_file_tree_file_name(package_path, asset_filename):
    return os.path.join(
        package_path.replace("/", "-"),
        asset_filename + ".json"
    )

def get_asset_file_tree_path(package_path, asset_name):
    return os.path.join(
        constants.VIT_DIR,
        constants.VIT_ASSET_TREE_DIR,
        gen_package_dir_name(package_path),
        "{}.json".format(asset_name)
    )

def gen_package_dir_name(package_path):
    return package_path.replace("/", "-")


def get_asset_file_tree(ssh_connection, path, package_path, asset_name):
    ssh_connection.get_vit_file(path, constants.VIT_PACKAGES)

    with PackageIndex(path) as package_index:
        package_file_name = package_index.get_package_tree_file_path(package_path)
    if not package_file_name:
        raise Package_AlreadyExists_E(package_path)

    ssh_connection.get(
        package_file_name,
        os.path.join(path, package_file_name)
    )

    with FilePackageTree(os.path.join(path, package_file_name)) as package_tree:
        asset_file_tree_path = package_tree.get_asset_tree_file_path(asset_name)
    if not asset_file_tree_path:
        raise Asset_NotFound_E(package_path, asset_name)

    ssh_connection.get(
        asset_file_tree_path,
        os.path.join(path, asset_file_tree_path)
    )
    return asset_file_tree_path

# LISTING DATA ---------------------------------------------------------------

def list_templates(path):
    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)
        with FileTemplate(path) as file_template:
            template_data = file_template.get_template_data()
    return template_data

def list_packages(path):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_vit_file(path, constants.VIT_PACKAGES)
        with PackageIndex(path) as package_index:
            ret = package_index.list_packages()
    return ret

def list_assets(path, package_path):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:
        tree_dir = os.path.join(constants.VIT_DIR, constants.VIT_ASSET_TREE_DIR)
        sshConnection.get(
            tree_dir,
            os.path.join(path, tree_dir),
            recursive=True
        )
        with PackageIndex(path) as package_index:
            package_tree_path = package_index.get_package_tree_file_path(package_path)
        with FilePackageTree(package_path) as package_tree:
            ret = package_tree.list_assets()
    return ret

def list_branchs(path, package_path, asset_name):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_tree_file(path, package_path, asset_name)
        with AssetTreeFile(path, package_path, asset_name) as treeFile:
            branchs = treeFile.list_branchs()
    return branchs

def list_tags(path, package_path, asset_name):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_tree_file(path, package_path, asset_name)
        with AssetTreeFile(path, package_path, asset_name) as treeFile:
            tags = treeFile.list_tags()
    return tags

