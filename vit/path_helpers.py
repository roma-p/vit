from vit import constants
from vit.custom_exceptions import *


def get_vit_repo_config_path(path, file_id):
    return os.path.join(path, constants.VIT_DIR, file_id)


def get_dot_vit_file(path, file_path):
    return os.path.join(path, constants.VIT_DIR, file_path)

# MISC ------------------------------------------------------------------------


def localize_path(local_path, raw_path):
    return os.path.join(local_path, raw_path)

# TEMPLATE --------------------------------------------------------------------


def get_index_template_path(local_repo_path):
    return get_dot_vit_file(local_repo_path, constants.VIT_TEMPLATE_CONFIG)


def get_template_path(template_file_name):
    return os.path.join(
        constants.VIT_DIR,
        constants.VIT_TEMPLATE_DIR,
        template_file_name
    )
