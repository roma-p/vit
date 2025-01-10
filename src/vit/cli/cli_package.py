from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli.argument_parser import add_subparser_from_parser_wrapper
from vit.cli import command_line_helpers
from vit.vit_lib import package
from vit.cli import logger


# PACKAGE ADD ----------------------------------------------------------------

def _callback_package_add(args):
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        package.create_package,
        "Could not create package {}".format(args.path),
        args.path, force_subtree=False  # TODO: add option for this.
    )
    if status:
        logger.log.info("Package successfully created at {}".format(args.path))
    return status


def _create_parser_package_add():
    parser = ArgumentParser('add')
    parser.help = 'add a new package on origin repository.'
    parser.description = """
--- vit PACKAGE ADD command ---

This command will add a new package to origin repository.

Package names HAS to be unique across all repository.
It can be named as a directory path, eg:
    asset/character/main_character/rig

The parent "package" has to exist to create an asset.
Use "-f" to reccursively create the packages and force package creation.
    """
    parser.epilog = """
examples:
    vit package add new/package
    vit package add new/package -f
    """
    parser.set_defaults(func=_callback_package_add)
    parser.add_argument(
        'path',  type=str,
        help='path of the new package.')
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="if parent directory does not exists, recursively create it. "
    )
    return parser


_parser_wrap_package_add = SubArgumentParserWrapper(
    arg_parser=_create_parser_package_add(),
    origin_connection_needed=True
)


# PACKAGE LIST ---------------------------------------------------------------

def _callback_package_list(args):
    status, packages = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        package.list_packages, "Could not list templates."
    )
    if status:
        if not packages:
            logger.log.info("no package found on origin repository.")
        else:
            logger.log.info("packages found on origin repository are:")
            for p in packages:
                logger.log.info("    - {}".format(p))
    return status


def _create_parser_package_list():
    parser = ArgumentParser('list')
    parser.help = 'list all packages found on origin repository.'
    parser.description = """
--- vit BRANCH LIST command ---

This command will list all existing packages on repository.
    """
    parser.epilog = """
examples:
    vit package list
    """
    parser.set_defaults(func=_callback_package_list)
    return parser


_parser_wrap_package_list = SubArgumentParserWrapper(
    arg_parser=_create_parser_package_list(),
    may_not_be_up_to_date=True
)


# MAIN -----------------------------------------------------------------------

def _create_parser_package():
    parser = ArgumentParser('package')
    parser.help = "manage package of assets."
    parser.description = """
--- vit PACKAGE management ---

From this menu are all the subcommands to manage vit packages.

A package is an asset container.
It is not (yet) versionned, only asets are.

Package names have to be unique on all repository
But, package can be named like a path would be. eg:
    "asset"
    "asset/charachter"
    "asset/character/main_charachter"
The name of the asset is the all string:
under the hood vit does not organize data as a directory hierarchy,
but it can be displayed as such to help artists organize their data.
    """
    package_subparsers = parser.add_subparsers(help='')
    add_subparser_from_parser_wrapper(package_subparsers, _parser_wrap_package_add)
    add_subparser_from_parser_wrapper(package_subparsers, _parser_wrap_package_list)
    return parser


PARSER_WRAPPER_PACKAGE = SubArgumentParserWrapper(
    arg_parser=_create_parser_package(),
)
