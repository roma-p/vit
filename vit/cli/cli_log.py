from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.cli import graph as graph_module
from vit.cli import log as log_module
import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def log_func(args):
    func = graph_module.main if args.graph else log_module.get_log_lines
    status, lines = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        func,
        "Could not log from {} {}.".format(args.package_path, args.asset),
        args.package_path, args.asset
    )
    if status:
        for line in lines:
            print(line)
    return status    


def create_parser():
    parser_log = ArgumentParser('log')
    parser_log.set_defaults(func=log_func)
    parser_log.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser_log.add_argument(
        "asset", type=str,
        help="id of the asset to log.")
    parser_log.add_argument(
        "-g", "--graph", action="store_true",
        help="log graph instead of historic of commit."
    )
    return parser_log
