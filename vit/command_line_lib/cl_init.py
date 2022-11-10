import argparse
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import repo_init_clone

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def init_func(args):
    status, _ = command_line_helpers.execute_vit_command(
        repo_init_clone.init_origin,
        "Could not initialize repository {}:".format(args.name),
        args.name
    )
    if status:
        log.info("Repository successfully initialized at {}".format(args.name))
    return status


def create_parser():
    parser_init = argparse.ArgumentParser('init')
    parser_init.set_defaults(func=init_func)
    parser_init.add_argument(
        'name', type=str,
        help='name of the repository. Will create a directory named as'
             'such in current directory.'
    )
    return parser_init
