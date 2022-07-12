import paramiko
from scp import SCPClient
from paramiko.auth_handler import AuthenticationException, SSHException
from getpass import getpass
import logging

log = logging.getLogger()

class SCPWrapper(object): 

    def __init__(self, server, port, user): 
        self.server = server
        self.port = port
        self.user = user

    def __enter__(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        password = getpass("{}'s password: ".format(self.user))
        try: 
            self.ssh_client.connect(self.server, self.port, self.user, password)
        except AuthenticationException:
            log.error("authentification error connecting to host.")
        except Exception:
            log.error("unpredicted behaviours happened connecting to host.")
        else:
            self.scp_client = SCPClient(self.ssh_client.get_transport())
            return self.scp_client

    def __exit__(self, type, value, traceback):
        self.scp_client.close()
        self.ssh_client.close()
