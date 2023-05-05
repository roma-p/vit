from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.vit_lib import tag
from vit.cli.logger import log


# TODO : tagging shall return name of tag. (for versionned tag and deplay.)


def tag_add(args):

    if args.annotated and args.versionned:
        log.error("inconsistent tag type")
        log.info("a tag is either lightweight (default),"
            " annotated (-a) or versionned (-v)"
        )
        return False

    if args.branch and args.commit:
        log.error("inconsistent tag target")
        log.info("a tag target is either a branch (-b) or a commit (-c)")
        return False

    if not args.name and (args.annotated or not args.versionned):
        log.error("no name set for tag")
        log.info("setting a name (-n) is required"
            " for lightweight and annotated tag"
        )
        return False

    if not args.message and (args.annotated or args.versionned):
        log.error("a commit message is required to create an annotated tag.")
        log.info("use -m to add a commit message")
        return False

    if args.versionned and args.increment is None:
        log.error("no increment set for versionned tag")
        log.info("set increment index (-i) forthe version of the tag.")
        return False

    if args.increment and (args.increment < 0 or args.increment) > 2:
        log.error("valid increment index are: 0, 1 and 2.")
        return False

    func = None
    kargs = {
        "package_path": args.package_path,
        "asset_name": args.asset,
        "branch": args.branch
    }

    if args.annotated:
        func = tag.create_tag_annotated_from_branch
        kargs["tag_name"] = args.name
        kargs["message"]  = args.message
    elif args.versionned:
        func = tag.create_tag_auto_from_branch
        kargs["message"]  = args.message
        kargs["update_idx"] = args.increment
    else:
        func = tag.create_tag_light_from_branch
        kargs["tag_name"] = args.name

    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        func,
        "Could not create tag for asset {}".format(args.asset),
        **kargs
    )
    if status:
        log.info("Successfully tagged {} {} from {}".format(
            args.package_path, args.asset, args.branch
        ))
    return status


def tag_list(args):

    status, tags = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        tag.list_tags,
        "Could not list tags for assets {} {}.".format(
            args.package_path,
            args.asset),
        args.package_path, args.asset
    )
    if status:
        if not tags:
            log.info("No tag found for asset {} {}".format(
                args.package_path,
                args.asset
            ))
        else:
            log.info("tags of {} {}".format(args.package_path, args.asset))
            for t in tags:
                log.info("    - {}".format(t))
    return status


def create_parser():
    parser_tag = ArgumentParser('tag')
    tag_subparsers = parser_tag.add_subparsers(help='')
    # -- ADD TAG --
    parser_tag_add = tag_subparsers.add_parser(
        'add',
        help='add a new tag on the given asset.'
    )
    parser_tag_add.set_defaults(func=tag_add)
    parser_tag_add.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset."
    )
    parser_tag_add.add_argument(
        "asset", type=str,
        help="id of the asset to tag."
    )
    parser_tag_add.add_argument(
        "-b", "--branch", type=str,
        help="id of the branch to tag."
    )
    parser_tag_add.add_argument(
        "-c", "--commit", type=str,
        help="id of the commit to tag"
    )
    parser_tag_add.add_argument(
        "-n", "--name", type=str,
        help="name of the tag that will be created."
             " required for both annotated and lightweight tag."
             " not for versionned tag where naming is automatic."
    )
    parser_tag_add.add_argument(
        "-a", "--annotated", action="store_true",
        help="will create an annotated commit. Default is lightweight."
    )
    parser_tag_add.add_argument(
        "-v", "--versionned", action="store_true",
        help="will create a versionned commit. Default is lightweight."
    )
    parser_tag_add.add_argument(
        "-i", "--increment", type=int,
        help="id of the digit version to increment."
             " 0 is major, 1 is minor, 2 is patch."
             " Required for versionned tag, not for lightweight and annotated tags."
    )
    parser_tag_add.add_argument(
        "-m", "--message", type=str,
        help="message for commit that will be created when tagging"
             "required for annotated and versionned commits. Not for lightweight."
    )
    # -- LIST TAGS --
    parser_tag_list = tag_subparsers.add_parser(
        'list', help='list tags of given assets.')
    parser_tag_list.set_defaults(func=tag_list)
    parser_tag_list.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser_tag_list.add_argument(
        "asset", type=str,
        help="id of the asset to tag.")
    return parser_tag
