import os
import shutil
import subprocess

import logging
log = logging.getLogger()


class FakeSSHConnection(object):

    def __init__(self, server, user):
        self.server = server
        self.user = user
        self.ssh_link = "{}@{}".format(
            self.user,
            self.server
        )
        self._open = False

    def __enter__(self):
        status = self.open_connection()
        return self if status else None

    def __exit__(self, t, value, traceback):
        self.close_connection()

    def open_connection(self):
        self._open = True
        return True

    def close_connection(self):
        self._open = False
        return

    def check_is_open(self):
        return self._open

    def check_is_lock(self):
        return self.exists(self.lock_file_path)

    def put(self, src, dst, recursive=False):
        self.copy(src, dst, recursive)

    def get(self, src, dst, recursive=False):
        self.copy(src, dst, recursive)

    def copy(self, src, dst, recursive=False):
        if recursive:
            parent_dir = os.path.dirname(dst)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy(src, dst)

    def exec_command(self, cmd):
        cmd_as_list = [i for i in cmd.split(" ") if i != ""]
        try:
            ret = subprocess.run(cmd_as_list, capture_output=True)
        except Exception:
            return False
        else:
            return not bool(ret.returncode)
