import argparse
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import asset

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def asset_list(args):
    status, assets = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        asset.list_assets,
        "Could not list assets for package {}.".format(args.package),
        args.package
    )
    if status:
        if not assets:
            log.info("No assets found on origin repository.")
        else:
            log.info("Assets found on origin for package {} repository are:".format(
                args.package))
            for a in assets:
                log.info("    - {}".format(a))
    return status


def create_parser():
    parser_list = argparse.ArgumentParser('list')
    parser_list.set_defaults(func=asset_list)
    parser_list.add_argument(
        "package", type=str,
        help="path to the package containing the asset."
    )
    return parser_list
