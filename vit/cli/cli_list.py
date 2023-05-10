from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.vit_lib import asset
import logging
log = logging.getLogger("vit")


def _callback_asset(args):
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


def _create_parser_list():
    parser = ArgumentParser('list')
    parser.set_defaults(func=_callback_asset)
    parser.help ="list all assets found on origin repository for given package."
    parser.description = """
--- vit LIST command ---

This command will list all existing asset of an existing package.
"""
    parser.epilog = """
examples:
    vit list package_1
    """
    parser.add_argument(
        "package", type=str,
        help="path to the package containing the asset."
    )
    return parser


PARSER_WRAPPER_LIST = SubArgumentParserWrapper(
    arg_parser=_create_parser_list(),
    may_not_be_up_to_date=True
)
