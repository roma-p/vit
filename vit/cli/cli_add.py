from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.vit_lib import asset

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def create_asset_from_template(package, asset_name, template):

    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        asset.create_asset_from_template,
        "Could not create asset {}".format(asset_name),
        package, asset_name, template
    )
    if status:
        log.info("Asset {} successfully created at {}".format(
            asset_name, package)
        )
    return status


def create_asset_from_file(package, asset_name, file):

    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        asset.create_asset_from_file,
        "Could not create asset {}".format(asset_name),
        package, asset_name, file
    )
    if status:
        log.info("Asset {} successfully created at {}".format(
            asset_name, package)
        )
    return status


def add(args):
    if args.template:
        return create_asset_from_template(
            args.package,
            args.asset,
            args.template
        )
    elif args.file:
        return create_asset_from_file(
            args.package,
            args.asset,
            args.file
        )
    else:
        log.info("Missing argument: either --template or --file")
        return False


def create_parser():
    parser_add = ArgumentParser('add')
    parser_add.set_defaults(func=add)
    parser_add.add_argument(
        "package", type=str,
        help="path of the package in which to add asset.")
    parser_add.add_argument(
        "asset", type=str,
        help="id of the asset. Asset's ids have to be unique by package.")
    parser_add.add_argument(
        "-t", "--template", type=str,
        help="id of the template from which to create the asset.")
    parser_add.add_argument(
        "-f", "--file", type=str,
        help="path to the file from which create asset from.")
    return parser_add
