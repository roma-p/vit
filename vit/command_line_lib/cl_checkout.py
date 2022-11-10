import argparse
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import checkout

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def checkout_func(args):
    not_none = []
    for arg in (args.branch, args.tag, args.commit):
        if arg is not None:
            not_none.append(arg)
    if len(not_none) > 2:
        log.error("invalid combination of options during fetching")
        log.error("checkout using exclusively one this option:"
            "  --branch or --tag or --commit"
        )
        return False
    if args.editable and args.tag:
        log.error("can't checkout a tag as editable")
        return False
    if args.editable and args.commit:
        log.error("can't checkout a commit as editable")
        return False

    kargs = {
        "package_path": args.package,
        "asset_name": args.asset,
        "rebase": args.reset
    }

    if args.branch:
        func = checkout.checkout_asset_by_branch
        kargs["branch"] = args.branch
        kargs["editable"] = args.editable
    elif args.tag:
        func = checkout.checkout_asset_by_tag
        kargs["tag"] = args.tag
    elif args.commit:
        func = checkout.checkout_asset_by_commit
        kargs["commit"] = args.commit

    status, checkout_file = command_line_helpers.execute_vit_command(
        func, "Could not checkout asset {}.".format(args.asset), **kargs
    )
    if status:
        log.info("asset {} successfully checkout at {}".format(
            args.asset, checkout_file))
    return status


def create_parser():
    parser_checkout = argparse.ArgumentParser('checkout')
    parser_checkout.set_defaults(func=checkout_func)
    parser_checkout.add_argument(
        "package", type=str,
        help="path to the package containing the asset."
    )
    parser_checkout.add_argument(
        "asset", type=str,
        help="id of the asset to fetch."
    )
    parser_checkout.add_argument(
        "-b", "--branch", default=None,
        help="if used, will fetch the latest commit from the given branch."
    )
    parser_checkout.add_argument(
        "-t", "--tag", default=None,
        help="if used, will fetch the given tag of the asset."
    )
    parser_checkout.add_argument(
        "-c", "--commit", default=None,
        help="if used, will fetch the commit reference of the asset."
    )
    parser_checkout.add_argument(
        "-e", "--editable", action="store_true",
        help="checkout the asset as 'editable': user will be the only one"
             " able to commit. Only works when fetching by branch."
    )
    parser_checkout.add_argument(
        "-r", "--reset", action="store_true",
        help="if the asset is already check out on local repository: "
             "will discard all changes."
    )
    return parser_checkout
