import os
import argparse
from vit.custom_exceptions import VitCustomException
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import repo_init_clone

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def init_func(args):
    path = os.path.join(os.getcwd(), args.name)
    try:
        repo_init_clone.init_origin(path)
    except VitCustomException as e:
        log.error("Could not initialize repository {}: ".format(path))
        return False
    else:
        log.info("Repository successfully initialized at {}".format(path))
        return True


def create_parser():
    parser_init = argparse.ArgumentParser('init')
    parser_init.set_defaults(func=init_func)
    parser_init.add_argument(
        'name', type=str,
        help='name of the repository. Will create a directory named as'
             'such in current directory.'
    )
    return parser_init
