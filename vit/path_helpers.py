import os
from vit import constants

def get_vit_file_config_path(path, file_id):
    return os.path.join(path, constants.VIT_DIR, file_id)
