import paramiko
from scp import SCPClient
from paramiko.auth_handler import AuthenticationException, SSHException
from getpass import getpass
import os

import logging
log = logging.getLogger()

class SSHConnection(object):

    port = 22

    def __init__(self, server, user):
        self.server = server
        self.user = user

    def __enter__(self):
        status = self.open_connection()
        return self if status else None

    def __exit__(self, type, value, traceback):
        self.close_connection()

    def open_connection(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        password = getpass("{}'s password: ".format(self.user))
        try:
            self.ssh_client.connect(self.server, self.port, self.user, password)
        except AuthenticationException:
            log.error("authentification error connecting to host.")
            return False
        except Exception:
            log.error("unpredicted behaviours happened connecting to host.")
            return False

        self.scp_client = SCPClient(self.ssh_client.get_transport())
        return True

    def close_connection(self):
        self.scp_client.close()
        self.ssh_client.close()

    def put(self, *args, **kargs):
        return self.scp_client.put(*args, **kargs)

    def get(self, *args, **kargs):
        return self.scp_client.get(*args, **kargs)

    def exec_command(self, command):
        try:
            ret = self.ssh_client.exec_command(command)
        except SSHException:
            return False
        else:
            stdout = ret[1].readlines()
            stderr = ret[2].readlines()
            return not len(stderr)>0

