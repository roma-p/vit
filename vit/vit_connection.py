import os

from vit import constants
from vit.file_asset_tree_dir import AssetTreeFile
from vit import file_config
from vit.ssh_connection import SSHConnection
import logging
log = logging.getLogger()

class VitConnection(object):

    SSHConnection = SSHConnection 
    lock_file_path = os.path.join(constants.VIT_DIR, ".lock")

    def __init__(self, server, origin_path, user):
        self.origin_path = origin_path
        self.ssh_connection = self.SSHConnection(server, user)

    def __enter__(self):
        if not self.ssh_connection.open_connection():
            return None
        if self.is_lock():
            log.error("origin repo already beeing modified by someone")
            return None
        self.lock()
        return self

    def __exit__(self, type, value, traceback):
        self.unlock()
        self.ssh_connection.close_connection()

    # -- Managing lock -------------------------------------------------------

    def is_lock(self):
        return self.exists(self._format_path(self.lock_file_path))

    def lock(self):
        return self.touch(self._format_path(self.lock_file_path))

    def unlock(self):
        return self.rm(self._format_path(self.lock_file_path))

    # -- SCP Commands --------------------------------------------------------

    def put(self, src, dst, *args, **kargs):
        return self.ssh_connection.put(
            src, self._format_path(dst),
            *args, **kargs
        )

    def get(self, src, dst, *args, **kargs):
        return self.ssh_connection.get(
            self._format_path(src), dst,
            *args, **kargs
        )

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

    def _format_path(self, path):
        return os.path.join(self.origin_path, path)

    def get_tree_file(self, path, package_path, asset_name):
        src = AssetTreeFile("", package_path, asset_name).asset_tree_file_path
        dst = AssetTreeFile(path, package_path, asset_name).asset_tree_file_path
        return self.get(src, dst, recursive=True)

    def put_tree_file(self, path, package_path, asset_name):
        dst = AssetTreeFile("", package_path, asset_name).asset_tree_file_path
        src = AssetTreeFile(path, package_path, asset_name).asset_tree_file_path
        return self.put(src, dst, recursive=True)

    def create_tree_dir(self, package_path):
        p = AssetTreeFile("", package_path, None).get_package_file_tree_path()
        if self.exists(p):
            return True
        return self.mkdir(p, p=True)

    # -- Shell Commands ------------------------------------------------------

    # won't work on windows shell.
    def exists(self, path):
        return self.ssh_connection.exec_command(
            "ls {}".format(self._format_path(path)))

    def mkdir(self, path, p=False):
        command = "mkdir "
        if p: command += "-p "
        command += self._format_path(path)
        return self.ssh_connection.exec_command(command)

    def touch(self, path):
        return self.ssh_connection.exec_command(
            "touch " + self._format_path(path))

    def rm(self, path, r=False):
        command = "rm "
        if r: command += "-r "
        command += self._format_path(path)
        return self.ssh_connection.exec_command(command)

    def cp(self, src, dst, r=False):
        src = self._format_path(src)
        dst = self._format_path(dst)
        command = "cp "
        if r: command += "-r "
        command = "{} {} {}".format(command, src, dst)
        return self.ssh_connection.exec_command(command)

    # -- Private -------------------------------------------------------------

    def _format_path(self, path):
        return os.path.join(self.origin_path, path)

def ssh_connect_auto(path):
    host, origin_path, user = file_config.get_origin_ssh_info(path)
    return VitConnection(host, origin_path, user)
