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

    def __enter__(self):
        status = self.open_connection()
        return self if status else None

    def __exit__(self, t, value, traceback):
        self.close_connection()

    def open_connection(self):
        return True

    def close_connection(self):
        return


    # FIXME: put and get not properly mocked, some cases not handled yet.

    def put(self, src, dst, recursive=False):
        shutil.copy(src, dst)

    def get(self, src, dst, recursive=False):
        if recursive:
            if os.path.isdir(src):
                if os.path.exists(dst):
                    return True
                return shutil.copytree(src, dst)
            elif not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
        shutil.copy(src, dst)

    def exec_command(self, cmd):
        cmd_as_list = [i for i in cmd.split(" ") if i != ""]
        try:
            ret = subprocess.run(cmd_as_list, capture_output=True)
        except Exception:
            return False
        else:
            return not bool(ret.returncode)
