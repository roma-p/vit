from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.vit_lib import rebase
from vit.cli import logger


# TODO : REBASE FROM TAG!

def _callback_rebase(args):
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
        logger.log.info("successfully {}".format(_str))
    return status


def _create_parser_rebase():
    parser = ArgumentParser('rebase')
    parser.set_defaults(func=_callback_rebase)
    parser.help = "will add a new commit on branch, identical to the one given."
    parser.description = """
--- vit REBASE command ---

This command is to "rebase" a branch to a given commit from its commit id.

What rebasing does is copying the file referenced by the commit, and use it
to create a new commit on a branch that reference the copy.

This way, no history is lost, it does not "reset" the branch by deleting
previous commit.

The commit you are rebasing to does not even have to belong to the target branch,
it can come from another branch.
It has to belong to the same asset as the branch though.
    """
    parser.epilog = """
examples:
-> rebasing
    vit rebase package_1 asset_A some_branch asset_A-branch-AEBDA535A6DV
"""
    parser.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser.add_argument(
        "asset", type=str,
        help="id of the asset to rebase.")
    parser.add_argument(
        "branch", type=str,
        help="id of the branch to rebase.")
    parser.add_argument(
        "commit", type=str,
        help="id of the commit to reset the branch to")
    return parser


PARSER_WRAPPER_REBASE = SubArgumentParserWrapper(
    arg_parser=_create_parser_rebase(),
    origin_connection_needed=True
)
