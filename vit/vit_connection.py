import os

from vit import constants
from vit.file_handlers import repo_config
from vit.ssh_connection import SSHConnection
from vit.custom_exceptions import RepoIsLock_E
import logging
log = logging.getLogger()


class VitConnection(object):

    SSHConnection = SSHConnection
    lock_file_path = os.path.join(constants.VIT_DIR, ".lock")

    def __init__(self, local_path, server, origin_path, user):
        self.local_path = local_path
        self.origin_path = origin_path
        self.ssh_connection = self.SSHConnection(server, user)

    def __enter__(self):
        self.ssh_connection.open_connection()
        if self.is_lock():
            raise RepoIsLock_E(self.ssh_connection.ssh_link)
        self.lock()
        return self

    def __exit__(self, t, value, traceback):
        self.unlock()
        self.ssh_connection.close_connection()

    @property
    def ssh_link(self):
        return self.ssh_connection.ssh_link    

    # -- Managing lock -------------------------------------------------------

    def is_lock(self):
        return self.exists(self._format_path_origin(self.lock_file_path))

    def lock(self):
        return self.touch(self._format_path_origin(self.lock_file_path))

    def unlock(self):
        return self.rm(self._format_path_origin(self.lock_file_path))

    # -- SCP Commands --------------------------------------------------------

    def put(self, src, dst, *args, **kargs):
        return self.ssh_connection.put(
            src, self._format_path_origin(dst),
            *args, **kargs
        )

    def get(self, src, dst, *args, **kargs):
        return self.ssh_connection.get(
            self._format_path_origin(src), dst,
            *args, **kargs
        )

    def put_auto(self, src, dst, *args, **kargs):
        return self.ssh_connection.put(
            self._format_path_local(src),
            self._format_path_origin(dst),
            *args, **kargs
        )

    def get_auto(self, src, dst, *args, **kargs):
        return self.ssh_connection.put(
            self._format_path_origin(src),
            self._format_path_local(dst),
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

    def create_dir_if_not_exists(self, dir_to_create):
        if self.exists(dir_to_create):
            return True
        return self.mkdir(dir_to_create, p=True)

    # -- Shell Commands ------------------------------------------------------

    # won't work on windows shell.
    def exists(self, path):
        return self.ssh_connection.exec_command(
            "ls {}".format(self._format_path_origin(path)))

    def mkdir(self, path, p=False):
        command = "mkdir "
        if p: command += "-p "
        command += self._format_path_origin(path)
        return self.ssh_connection.exec_command(command)

    def touch(self, path):
        return self.ssh_connection.exec_command(
            "touch " + self._format_path_origin(path))

    def rm(self, path, r=False):
        command = "rm "
        if r: command += "-r "
        command += self._format_path_origin(path)
        return self.ssh_connection.exec_command(command)

    def cp(self, src, dst, r=False):
        src = self._format_path_origin(src)
        dst = self._format_path_origin(dst)
        command = "cp "
        if r: command += "-r "
        command = "{} {} {}".format(command, src, dst)
        return self.ssh_connection.exec_command(command)

    # -- Private -------------------------------------------------------------

    def _format_path_origin(self, path):
        return os.path.join(self.origin_path, path)

    def _format_path_local(self, path):
        return os.path.join(self.local_path, path)


def ssh_connect_auto(path):
    host, origin_path, user = repo_config.get_origin_ssh_info(path)
    return VitConnection(path, host, origin_path, user)
