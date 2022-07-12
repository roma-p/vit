import os
import logging
log = logging.getLogger()

from vit import constants


def clone(origin_link, remote_path, username, remote=False):

    err_log = "error initialising origin repository:"

    if not os.path.exists(parent_dir):
        log.error(err_log)
        log.error("parent directory does not exists: {}".format(parent_dir))
        return False
    if os.path.exists(path): 
        log.error(err_log)
        log.error("directory already exists: {}".format(path))
        return False
    

    # check if origin_link hostname is similar to current hostname: remote= 


# don't want to wrapp scp using paramiko...
# calls using scp will be fine.
# to know if it is a vit directory: check .vit/config.json
# ORIGIN SHALL BE TRUE!!
# better way to do it: scp only ./vit/config.json
# if does not exist: fail.
# otherwise, edit it, and scp the directories...