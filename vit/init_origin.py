import os

import logging
log = logging.getLogger()

from vit import constants
from vit import vit_file_config

def init_origin(path):

    parent_dir = os.path.dirname(path)
    vit_dir = os.path.join(path, constants.VIT_DIR)

    err_log = "error initialising origin repository:"
    if not os.path.exists(parent_dir):
        log.error(err_log)
        log.error("parent directory does not exists: {}".format(parent_dir))
        return False
    if os.path.exists(path): 
        log.error(err_log)
        log.error("directory already exists: {}".format(path))
        return False
    else:
        os.mkdir(path)
        os.mkdir(vit_dir)
        vit_file_config.create_vite_fil_config(path)
        return True


def add_asset_container(path, container, *tasks): 
    if not _check_is_vit_dir: return False
    container_path = os.path.join(path, container)
    if os.path.exists(container_path): 
        log.error("cannot create asset container: {}, already exists.".format(
            container)
        )
        return False
    os.mkdir(container_path)
    for path in (os.path.join(container_path, t) for t in tasks): 
        os.mkdir(path)
    return True


def _check_is_vit_dir(path): 
    return os.path.exists(os.path.join(path, constants.VIT_DIR))
