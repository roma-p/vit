import os
import atexit

from vit import constants
from vit.file_handlers import repo_config
from vit.connection.ssh_connection import SSHConnection
from vit.custom_exceptions import RepoIsLock_E
import logging
log = logging.getLogger()


class VitConnection(object):

    SSHConnection = SSHConnection
    lock_file_path = os.path.join(constants.VIT_DIR, ".lock")
    instances = []

    def __init__(self, local_path, server, origin_path, user):

        self.local_path = local_path
        self.origin_path = origin_path
        self.ssh_connection = self.SSHConnection(server, user)
        self.__class__.instances.append(self)

    def open_connection(self):
        self.ssh_connection.open_connection()
        if self.check_is_lock():
            raise RepoIsLock_E(self.ssh_connection.ssh_link)
        self.lock()

    def close_connection(self):
        if not self.check_is_open():
            return
        if self.check_is_lock():
            self.unlock()
        self.ssh_connection.close_connection()

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, t, value, traceback):
        self.unlock()
        self.ssh_connection.close_connection()

    @property
    def ssh_link(self):
        return self.ssh_connection.ssh_link

    def check_is_open(self):
        return self.ssh_connection.check_is_open()

    # -- Managing lock -------------------------------------------------------

    def check_is_lock(self):
        return self.exists(self.lock_file_path)

    def lock(self):
        return self._touch(self.lock_file_path)

    def unlock(self):
        return self._rm(self.lock_file_path)

    # -- NEW API -------------------------------------------------------------

    def _get_data_from_origin(self, src, dst, is_editable=False):
        pass

    def _put_data_to_origin(self, src, dst, is_src_abritrary_path=False):
        pass

    # SHALL REPLACE: get_auto use for metadata /  get_vit_file
    def _get_metadata_from_origin(self, file):
        pass

    def _put_metadata_to_origin(self, stage_metadata_wrapper):
        if not self.check_is_lock():
            raise EnvironmentError()

    # -- SCP Commands --------------------------------------------------------


    # TODO: DEL ME, special assets shall be resolved from dir path!
    def put(self, src, dst, *args, **kargs):
        return self.ssh_connection.put(
            src, self._format_path_origin(dst),
            *args, **kargs
        )

    # TODO: DEL ME, special assets shall be resolved from dir path!
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
        return self.ssh_connection.get(
            self._format_path_origin(src),
            self._format_path_local(dst),
            *args, **kargs
        )

    def get_vit_file(self, vit_file_id):
        src = vit_file_id
        dst = os.path.join(self.local_path, vit_file_id)
        return self.get(src, dst)

    # del this... only way to put to origin is through a "stage"

    def put_vit_file(self, vit_file_id):
        if not self.check_is_lock():
            raise EnvironmentError()
        dst = vit_file_id
        src = os.path.join(self.local_path, vit_file_id)
        return self.put(src, dst)

    def create_dir_at_origin_if_not_exists(self, dir_to_create):
        if self.exists(dir_to_create):
            return True
        return self._mkdir(dir_to_create, p=True)

    def copy_file_at_origin(self, src, dst, r=False):
        return self._cp(src, dst, r)

    #  TODO : DEL ME AND USE SIMPLE GET INSTEAD.
    def fetch_asset_file(
            self, origin_file_path,
            local_file_path, do_copy=False):
        package_path_local = os.path.dirname(local_file_path)
        if not os.path.exists(package_path_local):
            os.makedirs(package_path_local)
        if do_copy:
            self.get(origin_file_path, local_file_path)

    def fetch_vit(self):
        self.get_auto(constants.VIT_DIR, constants.VIT_DIR, recursive=True)

    # -- Shell Commands ------------------------------------------------------
    # -- use for processing origin reposistory. ------------------------------

    # TODO : MAKE THIS WORK ON WINDOWS SHELL won't work on windows shell.
    def exists(self, path):
        return self.ssh_connection.exec_command(
            "ls {}".format(self._format_path_origin(path)))

    def _mkdir(self, path, p=False):
        command = "mkdir "
        if p:
            command += "-p "
        command += self._format_path_origin(path)
        return self.ssh_connection.exec_command(command)

    def _touch(self, path):
        return self.ssh_connection.exec_command(
            "touch " + self._format_path_origin(path))

    def _rm(self, path, r=False):
        command = "rm "
        if r:
            command += "-r "
        command += self._format_path_origin(path)
        return self.ssh_connection.exec_command(command)

    def _cp(self, src, dst, r=False):
        src = self._format_path_origin(src)
        dst = self._format_path_origin(dst)
        command = "cp "
        if r:
            command += "-r "
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


@atexit.register
def dispose_vit_connection():
    for instance in VitConnection.instances:
        if instance is not None:
            instance.close_connection()
