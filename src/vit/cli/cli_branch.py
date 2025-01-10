from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli.argument_parser import add_subparser_from_parser_wrapper
from vit.cli import command_line_helpers
from vit.vit_lib import branch
from vit.cli import logger


# BRANCH ADD -----------------------------------------------------------------


def _callback_branch_add(args):
    if args.commit and args.branch:
        logger.log.error("unconsistent argument: either branch from"
                  "branch (--branch) or commit (--commit), not both at one.")
        return False
    if not args.commit and not args.branch:
        logger.log.error("unconsistent argument: either branch from"
                  "branch (--branch) or commit (--commit), at least one.")
        return False

    kargs = {
        "package_path": args.package_path,
        "asset_name": args.asset,
        "branch_new": args.name,
        "create_tag": args.tag
    }

    if args.branch:
        kargs["branch_parent"] = args.branch
    if args.commit:
        kargs["commit_parent"] = args.commit

    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        branch.create_branch,
        "Could not create branch {}".format(args.name),
        **kargs
    )
    if status:
        logger.log.info("Successfully created branch {}.".format(args.name))
    return status


def _create_parser_branch_add():
    parser = ArgumentParser('add')
    parser.set_defaults(func=_callback_branch_add)
    parser.help = "add a new branch to a given asset."
    parser.description = """
--- vit BRANCH ADD command ---

This command is to create a new branch on a existing asset on origin repository.

It will not checkout the branch on current local repository,
it has to be done manually, see help on 'vit checkout' cmd.

A branch can be create either from:
    - a commit ID. To list all commits ID of an asset use 'vit log' cmd.
    - a branch: the commit currently referenced by the branch will be used.
You can not create a branch from a tag.

Branch names has to be unique by asset.

On branch creation, vit will create a commit.
Additionnaly, you can tag this first commit of the branch using "-t"
    """
    parser.epilog = """
examples:
-> creating a new branch from base branch and tagging it.
    vit branch add package_1 new_branch asset_A -b base -t
-> creating a new branch from a commit id:
    vit branch add package_1 new_branch asset_A -c package_1-98965532ABCEFAZ34D3
    """
    parser.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset."
    )
    parser.add_argument(
        "asset", type=str,
        help="id of the asset to branch."
    )
    parser.add_argument(
        "name", type=str,
        help="name of the new branch. name of branches has to be unique by asset."
    )
    parser.add_argument(
        "-b", "--branch", type=str,
        help="id of the branch to 'branch' from."
    )
    parser.add_argument(
        "-c", "--commit", type=str,
        help="id of the commit to 'commit' from."
    )
    parser.add_argument(
        "-t", "--tag", action="store_true",
        help="automatically create a versionned annotated tag at version 0.1.0"
    )
    return parser


_parser_wrap_branch_add = SubArgumentParserWrapper(
    arg_parser=_create_parser_branch_add(),
    origin_connection_needed=True
)


# BRANCH LIST ----------------------------------------------------------------

def _callback_branch_list(args):
    status, branches = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        branch.list_branches,
        "Could not list branches for assets {} {}.".format(args.package_path,
                                                           args.asset),
        args.package_path, args.asset
    )
    if status:
        if not branches:
            logger.log.info("No branches found for asset {} {}".format(
                args.package_path,
                args.asset
            ))
        else:
            logger.log.info("branches of {} {}".format(args.package_path, args.asset))
            for b in branches:
                logger.log.info("    - {}".format(b))
    return status


def _create_parser_branch_list():
    parser = ArgumentParser('list')
    parser.set_defaults(func=_callback_branch_list)
    parser.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser.help = "list branches of given assets."
    parser.description = """
--- vit BRANCH LIST command ---

This command will list all existing branch of an existing asset.
    """
    parser.epilog = """
examples:
    vit branch list package_1 asset_A
    """
    parser.add_argument(
        "asset", type=str,
        help="id of the asset to branch.")
    return parser


_parser_wrap_branch_list = SubArgumentParserWrapper(
    arg_parser=_create_parser_branch_list(),
    may_not_be_up_to_date=True
)


# MAIN -----------------------------------------------------------------------

def _create_parser_branch():
    parser = ArgumentParser('branch')
    parser.help = "manage branches of a given asset."
    parser.description = """
--- vit BRANCH management ---

From this menu are all the subcommands to manage vit branches.

A branch represents an independent line of development of an asset.

Every time a new version of an asset is submitted, using the "vit commit" cmd, 
a new commit is created on origin repository. Every commit maintains a reference
to its parent commit.
A branch is a reference to the last children of a chain of commit.

Multiple branches can exist in parrallel,
this way, work on a single artist can be parralilzed between artists.

Upon creation, asset will be created with default "base" branch
    """
    branch_subparsers = parser.add_subparsers(help='')
    add_subparser_from_parser_wrapper(branch_subparsers, _parser_wrap_branch_add)
    add_subparser_from_parser_wrapper(branch_subparsers, _parser_wrap_branch_list)
    return parser


PARSER_WRAPPER_BRANCH = SubArgumentParserWrapper(
    arg_parser=_create_parser_branch(),
)
