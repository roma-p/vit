import argparse
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import package

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def package_add(args):
    status, _ = command_line_helpers.execute_vit_command(
        package.create_package,
        "Could not create package {}".format(args.path),
        args.path, force_subtree=False # TODO: add option for this.
    )
    if status:
        log.info("Package successfully created at {}".format(args.path))
    return status


def package_list(args):
    status, packages = command_line_helpers.execute_vit_command(
        package.list_packages, "Could not list templates."
    )
    if status:
        if not packages:
            log.info("no package found on origin repository.")
        else:
            log.info("packages found on origin repository are:")
            for p in packages:
                log.info("    - {}".format(p))
    return status 


def create_parser():
    parser_package = argparse.ArgumentParser('package')
    package_subparsers = parser_package.add_subparsers(help='')
    # -- PACKAGE ADD --
    parser_package_add = package_subparsers.add_parser(
        'add',
        help='add a new package on origin repository.')
    parser_package_add.set_defaults(func=package_add)
    parser_package_add.add_argument(
        'path',  type=str,
        help='path of the new package.')
    parser_package_add.add_argument(
        "-f", "--force",
        action="store_true",
        help="if parent directory does not exists, recursively create it. "
    )
    # -- PACKAGE LIST --
    parser_package_list = package_subparsers.add_parser(
        'list',
        help='list all packages found on origin repository.')
    parser_package_list.set_defaults(func=package_list)
    return parser_package