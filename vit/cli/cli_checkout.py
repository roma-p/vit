from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.vit_lib import checkout

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def _callback_checkout(args):
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
        kargs["commit_file_name"] = args.commit

    status, checkout_file = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        func, "Could not checkout asset {}.".format(args.asset), **kargs
    )
    if status:
        log.info("asset {} successfully checkout at {}".format(
            args.asset, checkout_file))
    return status


def _create_parser_checkout():
    parser_checkout = ArgumentParser('checkout')
    parser_checkout.set_defaults(func=_callback_checkout)
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


PARSER_WRAPPER_CHECKOUT = SubArgumentParserWrapper(
    sub_command_name="checkout",
    arg_parser=_create_parser_checkout(),
    help="checkout an asset from origin to local repository.",
    description="""
--- vit CHECKOUT command ---

This command is to checkout asset from origin repository on your working copy.

The nature of a checkout will be different depending in which mode you cloned origin:
    - in local mode: the checkout will be a symbolinc link to a file on origin repo.
    - in remote mode: the checkout will be a copy of a file on origin repo. All
        the assets in dependancy will also be copied. copy is done using scp
        /!\ depending on asset size, checkout on remote mode can be very long.
    for more on local / remote mode: see help on 'vit clone' cmd.

There is several way to checkout an asset:
    - by branch: "-b", a branch is an active branch of devlopment on which artists iterates
                       -> to list branches use 'vit branch list' cmd
    - by commit: "-c", a past state of a branch, used to check previous version of an asset,
                        to revert branch to this commit...
    - by tag:    "-t", a capture point of the history, a "published" version of an asset.
                       -> to list tags use 'vit tag list' cmd

vit is unable to merge assets. Therefore to avoid conflict, it ensures that assets can
only be editable by one artist at at time.
By default, when you checkout an asset, it will be in 'read only' mode: you may be able to 
edit it in remote mode, but unable to commit it.

If you want to work on the asset, you have to checkout the asset in "editable mode" ("-e")
If someone is already working on it you won't be able to checkout the asset as editable.

Only branch can be checkout as editable, commit and tag are frozen.

To release the editable token, use either 'vit commit' or 'vit free' cmds.

If you have already checkout the asset but you want to discard the changes you made,
use the reset flag.
""",
    epilog="""
examples:

-> checkout the branch base of an asset as editable:
    vit checkout package_1 asset_A -b base -e
-> checkout the branch base just to delete some local modifications:
    vit checkout package_1 asset_A -b base -e -r
-> checkout a tag named: "delivery-v003":
    vit checkout package_1 asset_A -t delivery-v003
""",
    origin_connection_needed=True
)
