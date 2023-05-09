import os
from vit.custom_exceptions import VitCustomException, VitCustomException_FetchNeeded
from vit.connection.connection_utils import ssh_connect_auto
from vit import constants
from vit.cli.logger import log


def is_vit_repo():
    current_path = os.getcwd()
    s = os.path.exists(
        os.path.join(
            current_path,
            constants.VIT_DIR
        )
    )
    if not s:
        log.error("{} is not a vit repository".format(current_path))
    return s


def exec_vit_cmd_from_cwd_with_server(
        vit_command_func, error_mess,
        *args, **kargs):
    if not is_vit_repo():
        return False, None
    try:
        vit_connection = ssh_connect_auto(os.getcwd())
    except VitCustomException as e:
        log.error(error_mess)
        log.error(str(e))
        return False, None
    try:
        with vit_connection:
            ret = vit_command_func(vit_connection, *args, **kargs)
    except VitCustomException as e:
        log.error(error_mess)
        log.error(str(e))
        return False, None
    else:
        return True, ret


def exec_vit_cmd_from_cwd_without_server(
        vit_command_func, error_mess,
        *args, **kargs):
    if not is_vit_repo():
        return False, None
    try:
        ret = vit_command_func(os.getcwd(), *args, **kargs)
    except VitCustomException_FetchNeeded as e:
        log.error(error_mess)
        log.error(str(e))
        log.info("metadata may not be up to date, try: 'vit fetch' to update it.")
        return False, None
    except VitCustomException as e:
        log.error(error_mess)
        log.error(str(e))
        return False, None
    else:
        return True, ret
