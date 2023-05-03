from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.vit_lib import branch

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def branch_add(args):
    if args.commit and args.branch:
        log.error("unconsistent argument: either branch from"
                  "branch (--branch) or commit (--commit), not both at one.")
        return False
    if not args.commit and not args.branch:
        log.error("unconsistent argument: either branch from"
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
        log.info("Successfully created branch {}.".format(args.name))
    return status


def branch_list(args):
    status, branches = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        branch.list_branches,
        "Could not list branches for assets {} {}.".format(args.package_path,
                                                           args.asset),
        args.package_path, args.asset
    )
    if status:
        if not branches:
            log.info("No branches found for asset {} {}".format(
                args.package_path,
                args.asset
            ))
        else:
            log.info("branches of {} {}".format(args.package_path, args.asset))
            for b in branches:
                log.info("    - {}".format(b))
    return status


def create_parser():
    parser_branch = ArgumentParser('branch')
    branch_subparsers = parser_branch.add_subparsers(help='')

    # -- ADD BRANCH --
    parser_branch_add = branch_subparsers.add_parser(
        'add', help='add a new branch to a given asset.'
    )
    parser_branch_add.set_defaults(func=branch_add)
    parser_branch_add.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset."
    )
    parser_branch_add.add_argument(
        "asset", type=str,
        help="id of the asset to branch."
    )
    parser_branch_add.add_argument(
        "name", type=str,
        help="name of the new branch. name of branches has to be unique by asset."
    )
    parser_branch_add.add_argument(
        "-b", "--branch", type=str,
        help="id of the branch to 'branch' from."
    )
    parser_branch_add.add_argument(
        "-c", "--commit", type=str,
        help="id of the commit to 'commit' from."
    )
    parser_branch_add.add_argument(
        "-t", "--tag", action="store_true",
        help="automatically create a versionned annotated tag at version 0.1.0"
    )
    # -- LIST branches --
    parser_branch_list = branch_subparsers.add_parser(
        'list', help='list branches of given assets.')
    parser_branch_list.set_defaults(func=branch_list)
    parser_branch_list.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser_branch_list.add_argument(
        "asset", type=str,
        help="id of the asset to branch.")
    return parser_branch
