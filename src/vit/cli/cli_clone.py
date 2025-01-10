import os
from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import VitCustomException
from vit import py_helpers
from vit.vit_lib import repo_init_clone

from vit.cli import logger


def _callback_clone(args):

    origin_link = py_helpers.parse_ssh_link(args.origin_link)
    if not origin_link:
        logger.log.error("{} is not a valid ssh link")
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
        logger.log.error(err)
        logger.log.error(str(e))
        return False, None
    try:
        with vit_connection:
            repo_init_clone.clone(
                vit_connection, origin_path,
                clone_path, user, host
            )
    except VitCustomException as e:
        logger.log.error(err)
        logger.log.error(str(e))
        return False
    else:
        logger.log.info("{} successfully cloned at: {}".format(
            repository_name,
            clone_path
        ))
        return True


def _create_parser_clone():
    parser = ArgumentParser('clone')
    parser.set_defaults(func=_callback_clone)
    parser.add_argument(
        'origin_link', type=str,
        help='link to repository, formatted like a ssh link.\
            host:path/to/repository user@host:/path/to/repository'
        )
    parser.help = "clone a repository to current location."
    parser.description = """
--- vit CLONE command ---

This command is to create a working copy of an origin repository.
Unlike other most VCS, cloning won't copy all data from origin. It will only fetch metadata.
This is because of the enormous size a vfx project can reach.

Artist will have to manually 'checkout' each asset they intend to work on.
-> see help on 'vit checkout' cmd.

There is two way to clone a repository:
- local mode: the origin repository is on the same computer / network than your working copy.
    In local mode, artists will be working using symbolic links to the origin repository.
    Working this way allow to deal more easily with heavy files.
- remote mode: the origin repository can be reached via internet.
    In remote mode, assets (and their dependancy) are copied via a SSH connections.
    Suits remote work, but will be problematic has the size of the assets increases.
    (depends on your internet connection!)

/!\ Only remote mode is currently available.
""",
    parser.epilog = """
examples:

-> remote mode:
    vit clone user@someDomain:/path/to/origin
"""
    return parser


PARSER_WRAPPER_CLONE = SubArgumentParserWrapper(
    arg_parser=_create_parser_clone(),
)
