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

# INIT AND CLONING ------------------------------------------------------------

def init_origin(path):

    parent_dir = os.path.dirname(path)
    vit_dir = os.path.join(path, constants.VIT_DIR)
    vit_tmp_dir = os.path.join(path, constants.VIT_DIR, constants.VIT_TEMPLATE_DIR)

    err_log = "error initialising origin repository:"
    if not os.path.exists(parent_dir):
        log.error(err_log)
        log.error("parent directory does not exists: {}".format(parent_dir))
        return False
    if os.path.exists(path):
        log.error(err_log)
        log.error("directory already exists: {}".format(path))
        return False
    os.mkdir(path)
    os.mkdir(vit_dir)
    os.mkdir(vit_tmp_dir)

    file_config.create(path)
    file_template.create(path)
    file_file_track_list.create(path)
    return True

def clone(origin_link, clone_path, username, host="localhost"):

    err_log = "error initialising origin repository:"
    parent_dir = os.path.dirname(clone_path)
    if not os.path.exists(parent_dir):
        log.error(err_log)
        log.error("parent directory does not exists: {}".format(parent_dir))
        return False
    if os.path.exists(clone_path):
        log.error(err_log)
        log.error("directory already exists: {}".format(clone_path))
        return False
    if host != "localhost":
        log.error("not implemented sorry")
        return False

    os.mkdir(clone_path)
    vit_local_path = os.path.join(clone_path, constants.VIT_DIR)

    with VitConnection(host, origin_link, username) as ssh_connection:
        ssh_connection.get(
            os.path.join(origin_link, constants.VIT_DIR),
            vit_local_path,
            recursive=True
        )
    status = os.path.exists(vit_local_path)

    if status:
        file_config.edit_on_clone(
            clone_path,
            host,
            origin_link,
            username
        )
    return status


# CONFIGURING REPO ------------------------------------------------------------

def create_template_asset_maya(path, template_id, template_filepath):
    if not os.path.exists(template_filepath): return False
    if not template_filepath[-3:] == ".ma": return False

    with ssh_connect_auto(path) as sshConnection:

        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)

        id_already_exists = file_template.is_template_id_free(path, template_id)

        if id_already_exists:
            log.error("template id '{}' already exists".format(template_id))
            return False

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
        return True

# CREATING NEW DATA -----------------------------------------------------------

def create_package(path, package_path, force_subtree=False):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:

        origin_package_dir = package_path
        origin_parent_dir = os.path.dirname(origin_package_dir)

        if sshConnection.exists(origin_package_dir):
            log.error("directory already exists at package location: {}".format(
                origin_package_dir))
            return False
        if not sshConnection.exists(origin_parent_dir):
            if not force_subtree:
                return False
            elif not sshConnection.mkdir(origin_parent_dir):
                log.error("error creating dir: {}".format(origin_parent_dir))
                return False
        ret = sshConnection.mkdir(origin_package_dir)
    return ret

def create_asset_maya(
        path,
        package_path,
        asset_name,
        template_id):

    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection:

        if not sshConnection.exists(package_path):
            log.error("package not found at origin: {}".format(
                package_path))
            return False
        asset_path = os.path.join(package_path, asset_name)
        if sshConnection.exists(asset_path):
            log.error("already a package / asset {} at origin named {}".format(
                package_path, asset_name))
            return False

        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)

        template_data = file_template.get_template_path_from_id(path, template_id)

        if not template_data:
            log.error("template not found: {} ".format(template_id))
            return False
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

    return True

def fetch_asset(
        path, package_path,
        asset_name, branch,
        editable=False,
        rebase=False):

    with ssh_connect_auto(path) as sshConnection:
        sshConnection.get_tree_file(path, package_path, asset_name)

        with AssetTreeFile(path, package_path, asset_name) as treeFile:
            asset_filepath = treeFile.get_branch_current_file(branch)
            if editable:
                editor = treeFile.get_editor(asset_filepath)
                if editor:
                   return False #FIXME raise except here...
                _, _, user = file_config.get_origin_ssh_info(path)
                treeFile.set_editor(asset_filepath, user)
            sha256 = treeFile.get_sha256(asset_filepath)

        if asset_filepath is None: return False

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
        path, package_path,
        asset_name,
        os.path.join(
            package_path,
            asset_name_local),
        branch,
        editable=editable,
        origin_file_name=asset_filepath,
        sha256=sha256
    )
    return True

def commit_file(path, filepath, keep=False):
    # TODO: function to wrapp into "def commit" with a single connection
    #       when committing multiple files will be supported.

    file_data = file_file_track_list.get_files_data(path)
    if filepath not in file_data:
        return False # raise Untracked File Exc here.
    package_path, asset_name, branch, origin_file_name, editable, changes = file_data[filepath]
    if not editable:
        return False # raise NotEditable File here.
    if not changes:
        return False # raise NoChangesToCommit here.

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
        return True


def commit(path, keep=False):

    file_data = file_file_track_list.get_files_data(path)
    if not file_data:
        log.info("no changes to commit")
        return True

    _, _, user = file_config.get_origin_ssh_info(path)

    with ssh_connect_auto(path) as sshConnection:

        for (
                file_path,
                package_path,
                asset_name,
                branch,
                origin_file_name,
                editable,
                changes ) in file_data:

            if not changes:
                continue

            # FIXME: done multiple time for same asset...
            # need a buffer of tree file copied on a single commit.
            sshConnection.get_tree_file(path, package_path, asset_name)

            new_file_path = os.path.join(
                package_path,
                asset_name,
                _create_maya_filename(asset_name)
            )

            with AssetTreeFile(path, package_path, asset_name) as treeFile:

                treeFile.update_on_commit(
                    file_path,
                    new_file_path,
                    origin_file_name,
                    time.time(),
                    user,
                    keep
                )

            sshConnection.put(
                os.path.join(path, file_path),
                new_file_path
            )

            sshConnection.put_tree_file(path, package_path, asset_name)
            if not keep:
                os.remove(os.path.join(path, file_path))
                # TODO: another json that keep the file openned.
                file_file_track_list.remove_file(path, file_path)
    return True

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

            if branch_ref is None: return

            status = treeFile.create_new_branch_from_file(
                new_file_path,
                branch_parent,
                branch_new,
                time.time(),
                user
            )

        asset_dir_local_path = os.path.join(
            path,
            os.path.dirname(branch_ref)
        )

        if not os.path.exists(asset_dir_local_path):
            os.makedirs(asset_dir_local_path)

        sshConnection.get(
            branch_ref,
            os.path.join(path, branch_ref)
        )

        shutil.copy(
            os.path.join(path, branch_ref),
            os.path.join(path, new_file_path)
        )

        sshConnection.put(
            os.path.join(path, new_file_path),
            new_file_path
        )

        sshConnection.put_tree_file(path, package_path, asset_name)
        os.remove(os.path.join(path, branch_ref))
        file_file_track_list.remove_file(path, branch_ref)

def clean(path):

    file_data = file_file_track_list.get_files_data(path)

    non_commited_files= []
    for data in file_data:
        if data[5]:
            non_commited_files.append(data)
    if non_commited_files:
        log.error("can't clean local repository, some changes needs to be commit")
        for (
                file_path,
                package_path,
                asset_name,
                branch,
                editable,
                changes ) in non_commited_files:

            log.error("{}{} -> {} : {} ".format(package_path,asset_name,
                                                branch, file_path))
            return False
    for (file_path, _, _, _, _, _) in file_data:
        print(os.path.join(path, file_path))
        os.remove(os.path.join(path,
            file_path))
        return True

def get_status_local(path):
    return file_file_track_list.gen_status_local_data(path)

def _check_is_vit_dir(path):
    return os.path.exists(os.path.join(path, constants.VIT_DIR))

def _create_maya_filename(asset_name):
    return "{}-{}.ma".format(asset_name, uuid.uuid4())

def _format_asset_name_local(asset_name, branch):
    return "{}-{}.ma".format(asset_name, branch)
