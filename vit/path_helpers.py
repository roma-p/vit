import os
from vit import constants
from vit.custom_exceptions import *

# MISC ------------------------------------------------------------------------


def localize_path(local_path, raw_path):
    return os.path.join(local_path, raw_path)


# TODO: DELME
def get_template_path(template_file_name):
    return os.path.join(
        constants.VIT_TEMPLATE_DIR,
        template_file_name
    )
