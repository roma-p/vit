import os
import argparse
from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import VitCustomException
from vit import py_helpers
from vit.vit_lib import repo_init_clone

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def clone_func(args):

    origin_link = py_helpers.parse_ssh_link(args.origin_link)
    if not origin_link:
        log.error("{} is not a valid ssh link")
        return False
    user, host, origin_path = origin_link

    repository_name = os.path.basename(origin_path)
    clone_path = os.path.join(
        os.getcwd(),
        repository_name
    )

    err = "Could not clone repository {}:".format(origin_link)

    try:
        vit_connection = VitConnection(clone_path, host, origin_path, user)
    except VitCustomException as e:
        log.error(err)
        log.error(str(e))
        return False, None
    try:
        with vit_connection:
            repo_init_clone.clone(
                vit_connection, origin_path,
                clone_path, user, host
            )
    except VitCustomException as e:
        log.error(err)
        log.error(str(e))
        return False
    else:
        log.info("{} successfully cloned at: {}".format(
            repository_name,
            clone_path
        ))
        return True


def create_parser():
    parser_clone = argparse.ArgumentParser('clone')
    parser_clone.set_defaults(func=clone_func)
    parser_clone.add_argument(
        'origin_link', type=str,
        help='link to repository, formatted like a ssh link.\
            host:path/to/repository user@host:/path/to/repository'
        )
    return parser_clone
