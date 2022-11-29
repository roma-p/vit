import argparse
from vit.command_line_lib import command_line_helpers
from vit.command_line_lib import graph as graph_module
from vit.command_line_lib import log as log_module

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def log_func(args):
    func = graph_module.main if args.graph else log_module.get_log_lines
    status, lines = command_line_helpers.execute_vit_command(
        func,
        "Could not log from {} {}.".format(args.package_path, args.asset),
        args.package_path, args.asset
    )
    if status:
        for line in lines:
            print(line)
    return status    


def create_parser():
    parser_log = argparse.ArgumentParser('log')
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