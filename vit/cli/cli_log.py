from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.cli import graph as graph_module
from vit.cli import vit_log_utils


def _callback_log(args):
    func = graph_module.main if args.graph else vit_log_utils.get_log_lines
    status, lines = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        func,
        "Could not log from {} {}.".format(args.package_path, args.asset),
        args.package_path, args.asset
    )
    if status:
        for line in lines:
            print(line)
    return status


def _create_parser_log():
    parser = ArgumentParser('log')
    parser.set_defaults(func=_callback_log)
    parser.help = "log historic of given asset"
    parser.description = """
--- vit LOG command ---

This command will log all the commits for a given asset.

By default, this command will log all the commit sorted by date.
Logs can also be displayed as a graph using the '--graph' flag.
    """
    parser.epilog = """
examples:
    vit log package_1 asset_A
    vit log package_1 asset_A --graph
    """
    parser.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser.add_argument(
        "asset", type=str,
        help="id of the asset to log.")
    parser.add_argument(
        "-g", "--graph", action="store_true",
        help="log graph instead of historic of commit."
    )
    return parser


PARSER_WRAPPER_LOG = SubArgumentParserWrapper(
    arg_parser=_create_parser_log(),
    may_not_be_up_to_date=True
)
