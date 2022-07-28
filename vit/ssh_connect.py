import paramiko
from scp import SCPClient
from paramiko.auth_handler import AuthenticationException, SSHException
from getpass import getpass
from vit import constants
from vit import file_asset_tree_dir 
import logging
import os
from vit import file_config
log = logging.getLogger()

'''
to refacto :
    sshConnection -> for clone 
    vitConnection -> compose sshConnection, used for rest of time.
'''
class SSHConnection(object): 
    
    lock_file_path = os.path.join(constants.VIT_DIR, ".lock")
    ssh_port = 22

    def __init__(self, server, origin_path, user): 
        self.server = server
        self.user = user
        self.origin_path = origin_path

    def __enter__(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        password = getpass("{}'s password: ".format(self.user))
        try: 
            self.ssh_client.connect(self.server, self.ssh_port, self.user, password)
        except AuthenticationException:
            log.error("authentification error connecting to host.")
        except Exception:
            log.error("unpredicted behaviours happened connecting to host.")
            return None

        if self.is_lock():
            log.error("origin repo already beeing modified by someone")
            return None
        self.lock()
        self.scp_client = SCPClient(self.ssh_client.get_transport())
        return self 

    def __exit__(self, type, value, traceback):
        self.unlock()
        self.scp_client.close()
        self.ssh_client.close()

    def put(self, src, dst, *args, **kargs):
        return self.scp_client.put(
            src, self._format_path(dst),
            *args, **kargs
        )

    def get(self, src, dst, *args, **kargs):
        return self.scp_client.get(
            self._format_path(src), dst,
            *args, **kargs
        )

    # won't work on windows shell.
    def exists(self, path):
        return self._exec_command("ls {}".format(self._format_path(path)))
   
    def mkdir(self, path, p=False):
        command = "mkdir "
        if p: command += "-p "
        command += self._format_path(path)
        return self._exec_command(command)

    def touch(self, path):
        return self._exec_command("touch " + self._format_path(path))

    def rm(self, path, r=False):
        command = "rm "
        if r: command += "-r "
        command += self._format_path(path)
        return self._exec_command(command)

    def cp(self, src, dst, r=False):
        src = self._format_path(src)
        dst = self._format_path(dst)
        command = "cp "
        if r: command += "-r "
        command = "{} {} {}".format(command, src, dst) 
        return self._exec_command(command)

    def is_lock(self):
        return self.exists(self._format_path(self.lock_file_path))[0] 

    def lock(self):
        return self.touch(self._format_path(self.lock_file_path))[0]
    
    def unlock(self):
        return self.rm(self._format_path(self.lock_file_path))[0]

    def get_vit_file(self, path, vit_file_id):
        src = os.path.join(
            constants.VIT_DIR,
            vit_file_id
        )

        dst = os.path.join(
            path,
            constants.VIT_DIR,
            vit_file_id
        )
        return self.get(src, dst)

    def put_vit_file(self, path, vit_file_id):
        dst = os.path.join(
            constants.VIT_DIR,
            vit_file_id
        )

        src = os.path.join(
            path,
            constants.VIT_DIR,
            vit_file_id
        )
        return self.put(src, dst)

    def _exec_command(self, command):
        try:
            ret = self.ssh_client.exec_command(command)
        except SSHException:
            return False, None, None
        else:
            stdout = ret[1].readlines()
            stderr = ret[2].readlines()
            return not len(stderr)>0, stdout, stderr

    def _format_path(self, path):
        return os.path.join(self.origin_path, path)

    def get_tree_file(self, path, package_path, asset_name):
        src = file_asset_tree_dir.get_asset_file_tree_path("", package_path, asset_name)
        dst = file_asset_tree_dir.get_asset_file_tree_path(path, package_path, asset_name)
        return self.get(src, dst, recursive=True)

    def put_tree_file(self, path, package_path, asset_name):
        dst = file_asset_tree_dir.get_asset_file_tree_path("", package_path, asset_name)
        src = file_asset_tree_dir.get_asset_file_tree_path(path, package_path, asset_name)
        return self.put(src, dst, recursive=True)
    
    def create_tree_dir(self, package_path):
        p = file_asset_tree_dir.get_package_file_tree_path("", package_path)
        if self.exists(p)[0]:
            return True
        return self.mkdir(p, p=True)
            
def ssh_connect_auto(path):
    host, origin_path, user = file_config.get_origin_ssh_info(path)
    return SSHConnection(host, origin_path, user)
