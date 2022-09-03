import sys
import argparse
import logging

from vit import command_line_lib

logging.basicConfig()
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def init(args):
    return command_line_lib.init(args.name)


def clone(args):
    return command_line_lib.clone(args.origin_link)


def template_add(args):
    return command_line_lib.create_template(
        args.template,
        args.file,
        args.force
    )


def template_get(args):
    return command_line_lib.get_template(args.template)


def template_list(args):
    return command_line_lib.list_templates()


def package_add(args):
    return command_line_lib.create_package(args.path)


def package_list(args):
    return command_line_lib.list_packages()


def asset_list(args):
    return command_line_lib.list_assets(args.package)


def add(args):
    return command_line_lib.create_asset(
        args.package,
        args.asset,
        args.template
    )


def fetch(args):
    not_none = []
    for arg in (args.branch, args.tag, args.commit):
        if arg is not None:
            not_none.append(arg)
    if len(not_none) > 2:
        log.error("unvalid combinaison of options during fetching")
        log.error("fetch using exclusively one this option:  --branch or --tag or --commit")
        return False
    if args.editable and args.tag:
        log.error("can't fetch a tag as editable")
        return False
    if args.editable and args.commit:
        log.error("can't fetch a commit as editable")
        return False
    if args.branch:
        return command_line_lib.fetch_asset_by_branch(
            args.package,
            args.asset,
            args.branch,
            args.editable,
            args.reset
        )


def commit(args):
    return command_line_lib.commit(args.file, args.keep)


def branch_add(args):
    return command_line_lib.create_branch_from_origin_branch(
        args.package_path,
        args.asset,
        args.branch_new,
        args.branch_parent
    )


def branch_list(args):
    return command_line_lib.list_branchs(
        args.package_path,
        args.asset
    )


def tag_add(args):
    return command_line_lib.create_tag_light_from_branch(
        args.package_path,
        args.asset,
        args.branch,
        args.tag
    )


def tag_list(args):
    return command_line_lib.list_tags(
        args.package_path,
        args.asset
    )


def make_parser():

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
        help="if parent directory does not exists, reccursuvely create it. "
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
        "template", type=str,
        help="id of the template from wich to create the asset.")

    # FETCH ------------------------------------------------------------------
    parser_fetch = subparsers.add_parser(
        'fetch',
        help="fetch an asset from origin to local repository."
    )
    parser_fetch.set_defaults(func=fetch)
    parser_fetch.add_argument(
        "package", type=str,
        help="path to the package containing the asset."
    )
    parser_fetch.add_argument(
        "asset", type=str,
        help="id of the asset to fetch."
    )
    parser_fetch.add_argument(
        "-b", "--branch", default=None,
        help="if used, will fetch the latest commit from the given branch."
    )
    parser_fetch.add_argument(
        "-t", "--tag", default=None,
        help="if used, will fetch the given tag of the asset."
    )
    parser_fetch.add_argument(
        "-c", "--commit", default=None,
        help="if used, will fetch the commit reference of the asset."
    )
    parser_fetch.add_argument(
        "-e", "--editable", action="store_true",
        help="check the asset as 'editable': user will be the only one"
             " able to commit. Only works when fetching by branch."
    )
    parser_fetch.add_argument(
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

    # COMMIT - ----------------------------------------------------------------
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
        "-k", "--keep", action="store_true",
        help="local file won't be deleted on commit. if the file was fetch as"
             "'editable', the 'editable' token won't be released"
    )

    # BRANCH -----------------------------------------------------------------
    parser_branch = subparsers.add_parser(
        'branch',
        help="manage branches of a given asset.")
    branch_subparsers = parser_branch.add_subparsers(help='')

    # -- ADD BRANCH --  
    parser_branch_add = branch_subparsers.add_parser(
        'add', help='add a new branch to a given asset.')
    parser_branch_add.set_defaults(func=branch_add)
    parser_branch_add.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser_branch_add.add_argument(
        "asset", type=str,
        help="id of the asset to branch.")
    parser_branch_add.add_argument(
        "branch_new", type=str,
        help="id of the new branch. ids of branches has to be unique by assets.")
    parser_branch_add.add_argument(
        "branch_parent", type=str,
        help="id of the branch to 'branch' from.")

    # -- LIST BRANCHS -- 
    parser_branch_list = branch_subparsers.add_parser(
        'list', help='list branchs of given assets.')
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
        help='add a new tag on the given asset.')
    parser_tag_add.set_defaults(func=tag_add)
    parser_tag_add.add_argument(
        "package_path", type=str,
        help="path to the package containing the asset.")
    parser_tag_add.add_argument(
        "asset", type=str,
        help="id of the asset to tag.")
    parser_tag_add.add_argument(
        "branch", type=str,
        help="id of the branch to tag.")
    parser_tag_add.add_argument(
        "tag", type=str,
        help="id of the tag. tags ids have to be unique by assets.")

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

    return parser


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        s = args.func(args)
        if s: sys.exit(0)
        else: sys.exit(1)
    sys.exit(0)
