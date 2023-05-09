import os
from abc import ABC, abstractmethod

from vit import constants
from vit.path_helpers import localize_path
from vit.file_handlers.stage_metadata import StagedMetadata
from vit.connection.ssh_connection import SSHConnection
from vit.custom_exceptions import RepoIsLock_E
from vit.vit_lib.misc import file_name_generation


import logging
log = logging.getLogger()


class VitConnection(ABC):

    SSHConnection = SSHConnection
    lock_file_path = os.path.join(constants.VIT_DIR, ".lock")
    instances = []

    def __init__(self, local_path, server, origin_path, user):

        self.local_path = local_path
        self.origin_path = origin_path
        self.ssh_connection = self.SSHConnection(server, user)
        self.lock_manager = ContextManagerWrapper(
            self.lock,
            self.unlock
        )
        self.__class__.instances.append(self)

    # -- Managing connection -------------------------------------------------

    def open_connection(self):
        self.ssh_connection.open_connection()
        if self.check_is_lock():
            raise RepoIsLock_E(self.ssh_connection.ssh_link)

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
        return self.exists_on_origin(self.lock_file_path)

    def lock(self):
        return self._touch(self.lock_file_path)

    def unlock(self):
        if self.check_is_lock():
            return self._rm(self.lock_file_path)

    # -- Data transfer with origin api ---------------------------------------

    @abstractmethod
    def get_data_from_origin(
            self, src, dst,
            recursive=False,
            is_editable=False):
        raise NotImplementedError()

    @abstractmethod
    def put_data_to_origin(self, src, dst, is_src_abritrary_path=False):
        raise NotImplementedError()

    def get_metadata_from_origin(self, metadata_file_path, recursive=False):
        return self._ssh_get_wrapper(
            metadata_file_path,
            metadata_file_path,
            recursive
        )

    def get_metadata_from_origin_as_staged(
            self, metadata_file_path,
            file_handler_type, recursive=True):
        stage_file_name = file_name_generation.generate_stage_metadata_file_path(
            metadata_file_path
        )
        self._ssh_get_wrapper(
            metadata_file_path,
            stage_file_name,
            recursive=True
        )
        stage_file_name_local = localize_path(self.local_path, stage_file_name)
        return StagedMetadata(
            metadata_file_path,
            stage_file_name,
            stage_file_name_local,
            file_handler_type
        )

    def put_metadata_to_origin(
            self, stage_metadata_wrapper,
            keep_stage_file=False,
            recursive=False):
        if not self.check_is_lock():
            raise EnvironmentError()
        self._ssh_put_wrapper(
            stage_metadata_wrapper.stage_file_path,
            stage_metadata_wrapper.meta_data_file_path,
            recursive=recursive
        )
        self.get_metadata_from_origin(
            stage_metadata_wrapper.meta_data_file_path,
            recursive=recursive
        )
        if not keep_stage_file:
            stage_metadata_wrapper.remove_stage_metadata()

    def update_staged_metadata(self, stage_metadata_wrapper):
        self._ssh_get_wrapper(
            stage_metadata_wrapper.meta_data_file_path,
            stage_metadata_wrapper.stage_file_path
        )

    # command to be executed on origin ---------------------------------------

    def create_dir_at_origin_if_not_exists(self, dir_to_create):
        if self.exists_on_origin(dir_to_create):
            return True
        return self._mkdir(dir_to_create, p=True)

    def copy_file_at_origin(self, src, dst, r=False):
        return self._cp(src, dst, r)

    def exists_on_origin(self, path):
        # TODO : MAKE THIS WORK ON WINDOWS SHELL won't work on windows shell.
        return self._ls(path)

    # -- Private -------------------------------------------------------------

    def _format_path_origin(self, path):
        return os.path.join(self.origin_path, path)

    def _format_path_local(self, path):
        return os.path.join(self.local_path, path)

    def _ssh_get_wrapper(self, src, dst, *args, **kargs):
        return self.ssh_connection.get(
            self._format_path_origin(src),
            self._format_path_local(dst),
            *args, **kargs
        )

    def _ssh_put_wrapper(self, src, dst, *args, **kargs):
        return self.ssh_connection.put(
            self._format_path_local(src),
            self._format_path_origin(dst),
            *args, **kargs
        )

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

    def _ls(self, path):
        return self.ssh_connection.exec_command(
            "ls {}".format(self._format_path_origin(path)))


class ContextManagerWrapper(object):

    def __init__(self, hook_on_enter, hook_on_exit):
        self.hook_on_enter = hook_on_enter
        self.hook_on_exit = hook_on_exit

    def __enter__(self):
        self.hook_on_enter()
        return self

    def __exit__(self, t, value, traceback):
        self.hook_on_exit()
