import argparse
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import rebase

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


# TODO : REBASE FROM TAG! 

def rebase_func(args):
    _str = "rebased branch {} of asset {} to commit {}".format(
        args.branch,
        args.asset,
        args.commit
    )
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        rebase.rebase_from_commit, "Could not {}".format(_str),
        args.package_path, args.asset, args.branch, args.commit
    )
    if status:
        log.info("successfully {}".format(_str))
    return status 


def create_parser():
    parser_rebase = argparse.ArgumentParser('rebase')
    parser_rebase.set_defaults(func=rebase_func)
    parser_rebase.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser_rebase.add_argument(
        "asset", type=str,
        help="id of the asset to rebase.")
    parser_rebase.add_argument(
        "branch", type=str,
        help="id of the branch to rebase.")
    parser_rebase.add_argument(
        "commit", type=str,
        help="id of the commit to reset the branch to")
    return parser_rebase
