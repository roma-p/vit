import os
import paramiko
from scp import SCPClient
from vit.custom_exceptions import SSH_ConnectionError_E
from getpass import getpass

import logging
log = logging.getLogger()


class SSHConnection(object):

    port = 22

    def __init__(self, server, user):
        self.server = server
        self.user = user
        self.ssh_link = "{}@{}".format(
            self.user,
            self.server
        )
        self.ssh_client = None
        self.scp_client = None

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, t, value, traceback):
        self.close_connection()

    def open_connection(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        password = getpass("{}'s password: ".format(self.user))
        try:
            self.ssh_client.connect(self.server, self.port, self.user, password)
        except Exception as e:
            raise SSH_ConnectionError_E(self.ssh_link, e)
        else:
            self.scp_client = SCPClient(self.ssh_client.get_transport())

    def close_connection(self):
        self.scp_client.close()
        self.ssh_client.close()
        self.scp_client = None
        self.ssh_client = None

    def put(self, *args, **kargs):
        return self.scp_client.put(*args, **kargs)

    def get(self, *args, **kargs):
        dst = args[1]
        recursive = kargs.get("recursive")
        if recursive:
            parent_dir = os.path.dirname(dst)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
        return self.scp_client.get(*args, **kargs)

    def exec_command(self, command):
        ret = self.ssh_client.exec_command(command)
        stdout = ret[1].readlines()
        stderr = ret[2].readlines()
        return not len(stderr) > 0

    def check_is_open(self):
        return self.ssh_client is not None
