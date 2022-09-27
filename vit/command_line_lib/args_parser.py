import argparse
import logging

from vit.command_line_lib import commands

logging.basicConfig()
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def init(args):
    return commands.init(args.name)


def clone(args):
    return commands.clone(args.origin_link)


def template_add(args):
    return commands.create_template(
        args.template,
        args.file,
        args.force
    )


def template_get(args):
    return commands.get_template(args.template)


def template_list(args):
    return commands.list_templates()


def package_add(args):
    return commands.create_package(args.path)


def package_list(args):
    return commands.list_packages()


def asset_list(args):
    return commands.list_assets(args.package)


def add(args):
    if args.template:
        return commands.create_asset_from_template(
            args.package,
            args.asset,
            args.template
        )
    elif args.file:
        return commands.create_asset_from_file(
            args.package,
            args.asset,
            args.file
        )
    else:
        log.info("Missing argument: either --template or --file")
        return False

def checkout(args):
    not_none = []
    for arg in (args.branch, args.tag, args.commit):
        if arg is not None:
            not_none.append(arg)
    if len(not_none) > 2:
        log.error("invalid combination of options during fetching")
        log.error("checkout using exclusively one this option:  --branch or --tag or --commit")
        return False
    if args.editable and args.tag:
        log.error("can't checkout a tag as editable")
        return False
    if args.editable and args.commit:
        log.error("can't checkout a commit as editable")
        return False
    if args.branch:
        return commands.checkout_asset_by_branch(
            args.package, args.asset, args.branch,
            args.editable, args.reset
        )
    elif args.tag:
        return commands.checkout_asset_by_tag(
            args.package, args.asset,
            args.tag, args.reset
        )
    elif args.commit:
        return commands.checkout_asset_by_commit(
            args.package, args.asset,
            args.commit, args.reset
        )

def commit(args):
    if not args.message:
        log.error("no commit message specified")
        return False
    keep_file = args.keep_file or args.keep_editable
    keep_editable = args.keep_editable

    return commands.commit_func(
        args.file, args.message, keep_file, keep_editable
    )


def free(args):
    return commands.free(args.file)


def rebase(args):
    return commands.rebase_from_commit(
        args.package_path,
        args.asset,
        args.branch,
        args.commit
    )


def update(args):
    return commands.update_func(
        args.file,
        args.editable,
        args.reset
    )


def branch_add(args):
    return commands.create_branch_from_origin_branch(
        args.package_path,
        args.asset,
        args.branch_new,
        args.branch_parent,
        create_tag=args.tag
    )


def branch_list(args):
    return commands.list_branches(
        args.package_path,
        args.asset
    )


def tag_add(args):

    if args.annotated and args.versionned:
        log.error("inconsistent tag type")
        log.info("a tag is either lifgtweight (default), annotated (-a) or versionned (-v)")
        return False

    if args.branch and args.commit:
        log.error("inconsistent tag target")
        log.info("a tag target is either a branch (-b) or a commit (-c)")
        return False

    if not args.name and (args.annotated or not args.versionned):
        log.error("no name set for tag")
        log.info("setting a name (-n) is required for lightweight and annotated tag")
        return False

    if not args.message and (args.annotated or args.versionned):
        log.error("a commit message is required to create an annotated tag.")
        log.info("use -m to add a commit message")
        return False

    if args.versionned and args.increment is None:
        log.error("no increment set for versionned tag")
        log.info("set increment index (-i) forthe version of the tag.")
        return False

    if args.increment is not None and (args.increment < 0 or args.increment) > 2:
        log.error("valid increment index are: 0, 1 and 2.")
        return False

    if args.annotated:
        return commands.create_tag_annotated_from_branch(
            args.package_path, args.asset, args.branch,
            args.name, args.message
        )
    elif args.versionned:
        return commands.create_tag_auto_from_branch(
            args.package_path, args.asset, args.branch,
            args.name, args.message, args.increment
        )
    else:
        return commands.create_tag_light_from_branch(
            args.package_path, args.asset,
            args.branch, args.name
        )


def tag_list(args):
    return commands.list_tags(
        args.package_path,
        args.asset
    )


def info(args):
    return commands.info(args.file)


def log_func(args):
    if args.graph:
        return commands.graph_func(args.package_path, args.asset)
    else:
        return commands.log_func(args.package_path, args.asset)


def clean(args):
    return commands.clean_func()


def create_parser():

    parser = argparse.ArgumentParser(
        description='A VCS specialised for VFX data.'
    )
    subparsers = parser.add_subparsers(help='main commands are:')

    # INIT -------------------------------------------------------------------
    parser_init = subparsers.add_parser(
        'init',
        help='initialize a new VIT repository.'
    )
    parser_init.set_defaults(func=init)
    parser_init.add_argument(
        'name', type=str,
        help='name of the repository. Will create a directory named as'
             'such in current directory.'
    )

    # CLONE ------------------------------------------------------------------
    parser_clone = subparsers.add_parser(
        'clone',
        help='clone a repository to current location.'
    )
    parser_clone.set_defaults(func=clone)
    parser_clone.add_argument(
        'origin_link', type=str,
        help='link to repository, formatted like a ssh link.\
            host:path/to/repository user@host:/path/to/repository'
        )

    # TEMPLATE ---------------------------------------------------------------
    parser_template = subparsers.add_parser(
        'template',
        help='manage asset templates.'
    )
    template_subparsers = parser_template.add_subparsers(help='')

    # -- TEMPLATE ADD --
    parser_template_add = template_subparsers.add_parser(
        'add',
        help='add a new asset template to origin.'
    )
    parser_template_add.set_defaults(func=template_add)
    parser_template_add.add_argument(
        'template', type=str,
        help='identifier of the template. Template ids are unique.'
    )
    parser_template_add.add_argument(
        'file', type=str,
        help='path to the file to be used as asset template'
    )
    parser_template_add.add_argument(
        "-f", "--force",
        action="store_true",
        help="if template ids already exists, "
             "its template file will be overwritten"
    )

    # -- TEMPLATE GET --
    parser_template_get = template_subparsers.add_parser(
        'get',
        help='fetch template file locally from origin using its id')
    parser_template_get.set_defaults(func=template_get)
    parser_template_get.add_argument(
        'template', type=str,
        help='identifier of the template')

    # -- TEMPLATE LIST --
    parser_template_list = template_subparsers.add_parser(
        'list',
        help='list all templates found on origin repository.')
    parser_template_list.set_defaults(func=template_list)

    # PACKAGE ----------------------------------------------------------------
    parser_package = subparsers.add_parser(
        'package',
        help='manage package of assets.')
    package_subparsers = parser_package.add_subparsers(help='')

    # -- PACKAGE ADD --
    parser_package_add = package_subparsers.add_parser(
        'add',
        help='add a new package on origin repository.')
    parser_package_add.set_defaults(func=package_add)
    parser_package_add.add_argument(
        'path',  type=str,
        help='path of the new package.')
    parser_package_add.add_argument(
        "-f", "--force",
        action="store_true",
        help="if parent directory does not exists, recursively create it. "
    )

    # -- PACKAGE LIST --
    parser_package_list = package_subparsers.add_parser(
        'list',
        help='list all packages found on origin repository.')
    parser_package_list.set_defaults(func=package_list)

    # ADD --------------------------------------------------------------------
    parser_add = subparsers.add_parser(
        'add',
        help="add a new asset to origin repository"
    )
    parser_add.set_defaults(func=add)
    parser_add.add_argument(
        "package", type=str,
        help="path of the package in which to add asset.")
    parser_add.add_argument(
        "asset", type=str,
        help="id of the asset. Asset's ids have to be unique by package.")
    parser_add.add_argument(
        "-t", "--template", type=str,
        help="id of the template from which to create the asset.")
    parser_add.add_argument(
        "-f", "--file", type=str,
        help="path to the file from which create asset from.")


    # CHECKOUT ----------------------------------------------------------------
    parser_checkout = subparsers.add_parser(
        'checkout',
        help="checkout an asset from origin to local repository."
    )
    parser_checkout.set_defaults(func=checkout)
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

    # LIST  -----------------------------------------------------------------
    parser_list = subparsers.add_parser(
        'list',
        help='list all assets found on origin repository for given package.')
    parser_list.set_defaults(func=asset_list)
    parser_list.add_argument(
        "package", type=str,
        help="path to the package containing the asset."
    )

    # COMMIT -----------------------------------------------------------------
    parser_commit = subparsers.add_parser(
        'commit',
        help="commit changes done locally to an asset to origin repository."
             " By default: releases the 'editable' token and delete local."
    )
    parser_commit.set_defaults(func=commit)
    parser_commit.add_argument(
        "file", type=str,
        help="path of the file you want to commit."
    )
    parser_commit.add_argument(
        "-k", "--keep_file", action="store_true",
        help="local file won't be deleted on commit. if the file was fetch as"
             "'editable', the 'editable' token WILL be released"
    )
    parser_commit.add_argument(
        "-K", "--keep_editable", action="store_true",
        help="local file won't be deleted on commit. if the file was fetch as"
             "'editable', the 'editable' token WILL NOT be released"
    )
    parser_commit.add_argument(
        "-m", "--message",
        help="commit message"
    )

    # FREE -----------------------------------------------------------------
    parser_commit = subparsers.add_parser(
        'free',
        help="if an asset was checkout as editable, free the 'editable' token"
             "so that someone else can checkout the asset as 'editable'"
    )
    parser_commit.set_defaults(func=free)
    parser_commit.add_argument(
        "file", type=str,
        help="path of the file you want to free."
    )

    # REBASE -----------------------------------------------------------------
    parser_rebase = subparsers.add_parser(
        'rebase',
        help="will add a new commit on branch, identical to the one given."
    )
    parser_rebase.set_defaults(func=rebase)
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

    # UPDATE -----------------------------------------------------------------
    parser_update = subparsers.add_parser(
        'update',
        help="update checkout file to latest commit of branch."
             "also useful to make a checkout file editable"
    )
    parser_update.set_defaults(func=update)
    parser_update.add_argument(
        "file", type=str,
        help="path of the file you want to update."
    )
    parser_update.add_argument(
        "-e", "--editable", action="store_true",
        help="checkout the asset as 'editable': user will be the only one"
             " able to commit. Only works when fetching by branch."
    )
    parser_update.add_argument(
        "-r", "--reset", action="store_true",
        help="will discard and overwrite any change done locally to the asset."
    )

    # BRANCH -----------------------------------------------------------------
    parser_branch = subparsers.add_parser(
        'branch',
        help="manage branches of a given asset.")
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
        "branch_new", type=str,
        help="id of the new branch. ids of branches has to be unique by assets."
    )
    parser_branch_add.add_argument(
        "branch_parent", type=str,
        help="id of the branch to 'branch' from."
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

    # TAG --------------------------------------------------------------------

    # -- ADD TAG --

    parser_tag = subparsers.add_parser(
        'tag',
        help="manage tags of a given asset")
    tag_subparsers = parser_tag.add_subparsers(help='')
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
             "required for both annotated and lightweight commit."
             "not for versionned tag where naming is automatici."
    )
    parser_tag_add.add_argument(
        "-a", "--annotated", action="store_true",
        help="will create an anotated commit. Default is lightweight."
    )
    parser_tag_add.add_argument(
        "-v", "--versionned", action="store_true",
        help="will create a versionned commit. Default is lightweight."
    )
    parser_tag_add.add_argument(
        "-i", "--increment", type=int,
        help="id of the digit version to increment."
             "0 is major, 1 is minor, 2 is patch"
             "requird for versionned tag, not for lightweight and annotated tags."
    )
    parser_tag_add.add_argument(
        "-m", "--message", type=str,
        help="message for commit that will be created when tagging"
             "required for annotated and versionned commits. Not for lifgtweight."
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

    # INFO -------------------------------------------------------------------

    parser_info = subparsers.add_parser(
        'info', help='get information on a ref file.')
    parser_info.set_defaults(func=info)
    parser_info.add_argument(
        "file", type=str,
        help="path to the file to get info from.")

    # LOG --------------------------------------------------------------------

    parser_log = subparsers.add_parser(
        'log', help='log historic of given asset.')
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

    # CLEAN  -----------------------------------------------------------------

    parser_clean = subparsers.add_parser(
        'clean', help='remove files on local repositary that can safely be removed.')
    parser_clean.set_defaults(func=clean)

    # MACRO  -----------------------------------------------------------------

    return parser


