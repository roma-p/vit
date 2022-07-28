import os
import uuid
import shutil
import time

import logging
log = logging.getLogger()

from vit import py_helpers
from vit import constants
from vit.ssh_connect import SSHConnection, ssh_connect_auto

from vit import file_config
from vit import file_template
from vit import file_file_track_list
from vit import file_commit_list 
#from vit import file_asset_info
from vit import file_asset_tree_dir

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
    else:
        os.mkdir(path)
        os.mkdir(vit_dir)
        os.mkdir(vit_tmp_dir)

        file_config.create(path)
        file_template.create(path)
        file_file_track_list.create(path)
        file_commit_list.create(path)

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
    
    with SSHConnection(host, origin_link, username) as ssh_connection:
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

        file_template.reference_new_template(path, template_id, template_scn_dst)
        
        sshConnection.put_vit_file(path, constants.VIT_TEMPLATE_CONFIG)
       
        sshConnection.put(
            template_filepath,
            template_scn_dst
        )

# CREATING NEW DATA -----------------------------------------------------------

def create_package(path, package_path, force_subtree=False):
    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection: 

        origin_package_dir = package_path
        origin_parent_dir = os.path.dirname(origin_package_dir)
   
        out = sshConnection.exists(origin_package_dir)
        if out[0]: 
            log.error("directory already exists at package location: {}".format(
                origin_package_dir))
            return False
        out = sshConnection.exists(origin_parent_dir)    
        if not out[0]:
            if not force_subtree:
                return False
            else:
                out = sshConnection.mkdir(origin_parent_dir)
                if not out[0]:
                    log.error("error creating dir: {}".format(origin_parent_dir))
                    return False
        ret = sshConnection.mkdir(origin_package_dir)[0]
    return ret


def create_asset_maya(
        path,
        package_path,
        asset_name,
        template_id):

    if not _check_is_vit_dir(path): return False

    with ssh_connect_auto(path) as sshConnection: 
       
        out = sshConnection.exists(package_path)
        if not out[0]: 
            log.error("package not found at origin: {}".format(
                package_path))
            return False
        asset_path = os.path.join(package_path, asset_name)
        out = sshConnection.exists(asset_path)
        if out[0]:
            log.error("already a package / asset {} at origin named {}".format(
                package_path, asset_name))
            return False

        sshConnection.get_vit_file(path, constants.VIT_TEMPLATE_CONFIG)
        
        template_path = file_template.get_template_path_from_id(path, template_id)

        if not template_path:
            log.error("template not found: {} ".format(template_id))
            return False
        
        asset_path = os.path.join(package_path, asset_name)
        sshConnection.mkdir(asset_path)

        asset_file = "{}-{}.ma".format(asset_name, int(time.time()))
        sshConnection.cp(
            template_path,
            os.path.join(asset_path, asset_file)
        )
       
        _, _, user = file_config.get_origin_ssh_info(path)
        file_asset_tree_dir.create_asset_file_tree(
                path,
                package_path,
                asset_name,
                asset_file,
                user
        )
        
        sshConnection.create_tree_dir(package_path) 
        sshConnection.put_tree_file(path, package_path, asset_name)

    return True

# todo: version? branch? tag? 
def fetch_asset(path, package_path, asset_name, branch, editable=False):
    # 1 check existence of package and asset.
    # 2 copy asset in local. where to? in special subdir? 
    # 3 add to file tracker? register sha in 
    
    with ssh_connect_auto(path) as sshConnection: 
        sshConnection.get_tree_file(path, package_path, asset_name)
        branch_ref = file_asset_tree_dir.get_branch_current_file(
             path,
             package_path,
             asset_name, 
             branch
        )
        if branch_ref is None: return False
        
        os.makedirs(
            os.path.join(
                path,
                os.path.dirname(branch_ref)
            ),
        )

        sshConnection.get(
            branch_ref,
            os.path.join(path, branch_ref)
        )
    file_file_track_list.add_tracked_file(path, branch_ref)

def commit(local_path):
    pass 
    """
    files_to_commit = file_file_track_list.list_changed_files(local_path)
    files_to_commit += tuple(file_commit_list.get_files(local_path))
    files_to_commit = sorted(files_to_commit)
    host, origin_path, username = file_config.get_origin_ssh_info(local_path)

    with SCPWrapper(host, 22, username) as (ssh_client, scp_client):
        for file_path in files_to_commit:
            scp_client.put(
                os.path.join(local_path, file_path),
                os.path.join(origin_path, file_path),
                recursive=True)
    file_file_track_list.clean(local_path)
    file_commit_list.clean(local_path)
    """

def clean(path): 
    pass

    # list track files updates with sha 
    # if sha differs: new edition done to file
    # add it to the "to comit files"
    # for files not in "tocommit": clean. 


def asset_commit(path):
    pass


def asset_upgrade(): 
    pass

# a better name for package: package. 
# OK WAY BETTER: two entities: assets and packages. That's it. 
# to the user to organize their work with that.


def package_commit(asset_or_package):
    pass


def _check_is_vit_dir(path): 
    return os.path.exists(os.path.join(path, constants.VIT_DIR))

