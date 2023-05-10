import os
from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.custom_exceptions import VitCustomException
from vit.vit_lib import repo_init_clone
import logging
log = logging.getLogger("vit")


def _callback_init(args):
    path = os.path.join(os.getcwd(), args.name)
    try:
        repo_init_clone.init_origin(path)
    except VitCustomException as e:
        log.error("Could not initialize repository {}: ".format(path))
        return False
    else:
        log.info("Repository successfully initialized at {}".format(path))
        return True


def _create_parser_init():
    parser = ArgumentParser('init')
    parser.set_defaults(func=_callback_init)
    parser.help = "initialize a new VIT repository."
    parser.description = """
--- vit INIT command ---

This command will initialize a new ORIGIN repository.

Unlike git, vit is a centralized versionning system.
The origin repository will hold all the vfx data of the projects.
But, unlike a distributed versionning system, you can not directly work on it.
Its aim is only to hold all the vfx data of the projets and all its metadata.

To work on the project, you have to "clone" the repository: see "vit clone" cmd.
    """
    parser.add_argument(
        'name', type=str,
        help='name of the repository. Will create a directory named as'
             'such in current directory.'
    )
    return parser


PARSER_WRAPPER_INIT = SubArgumentParserWrapper(
    arg_parser=_create_parser_init(),
)
