import atexit
from vit.file_handlers import repo_config
from vit.connection.vit_connection import VitConnection
from vit.connection.vit_connection_local import VitConnectionLocal
from vit.connection.vit_connection_remote import VitConnectionRemote


def ssh_connect_auto(path):
    host, origin_path, user = repo_config.get_origin_ssh_info(path)
    vit_connection_type = {
        True: VitConnectionRemote,
        False: VitConnectionLocal
    }[repo_config.check_is_working_copy_remote(path)]
    return vit_connection_type(path, host, origin_path, user)


@atexit.register
def dispose_vit_connection():
    for instance in VitConnection.instances:
        if instance is not None:
            instance.close_connection()
