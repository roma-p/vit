import os
import logging
log = logging.getLogger()

from vit import constants
from vit import py_helpers
from vit.scp_wrapper import SCPWrapper


def clone(origin_link, clone_path, username, host="localhost"):

    err_log = "error initialising origin repository:"
    parent_dir = os.path.dirname(clone_path)
    if not os.path.exists(parent_dir):
        log.error(err_log)
        log.error("parent directory does not exists: {}".format(parent_dir))
        return False
    if os.path.exists(clone_path): 
        log.error(err_log)
        log.error("directory already exists: {}".format(clone_path))
        return False
    if host != "localhost": 
        log.error("not implemented sorry")
        return False
    
    os.mkdir(clone_path)
    vit_local_path = os.path.join(clone_path, constants.VIT_DIR)
    with SCPWrapper(host, 22, username) as scp_client:
        scp_client.get(
            os.path.join(origin_link, constants.VIT_DIR),
            vit_local_path,
            recursive=True
        )
    return os.path.exists(vit_local_path)

    # check if origin_link hostname is similar to current hostname: remote= 


# don't want to wrapp scp using paramiko...
# calls using scp will be fine.
# to know if it is a vit directory: check .vit/config.json
# ORIGIN SHALL BE TRUE!!
# better way to do it: scp only ./vit/config.json
# if does not exist: fail.
# otherwise, edit it, and scp the directories...