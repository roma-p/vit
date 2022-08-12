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
    return command_line_lib.create_template(args.name, args.file)

def template_get(args):
    return False

def package_add(args):
    return command_line_lib.create_package(args.path)

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

def tag_add(args):
    return command_line_lib.create_tag_light_from_branch(
        args.package,
        args.asset,
        args.branch,
        args.tag
    )

def make_parser():

    parser = argparse.ArgumentParser(description='manage vfx asset files.')
    subparsers = parser.add_subparsers(help='')

    # INIT -------------------------------------------------------------------
    parser_init = subparsers.add_parser(
        'init',
        help='initialize a new VIT repository'
    )
    parser_init.set_defaults(func=init)
    parser_init.add_argument(
        'name', type=str,
        help='name of the repository. Will create a directory named as such in current directory.'
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
    parser_template = subparsers.add_parser('template', help='')
    template_subparsers = parser_template.add_subparsers(help='')

    # -- TEMPLATE ADD --
    parser_template_add = template_subparsers.add_parser(
        'add',
        help='add a new asset template')
    parser_template_add.set_defaults(func=template_add)
    parser_template_add.add_argument(
        'name', type=str,
        help='identifier of the template. Has to be unique'
    )
    parser_template_add.add_argument(
        'file', type=str,
        help='path to the file to be used as asset template')

    # TODO: add the U option (or f) to force update of an existing template !!!!!!!

    # -- TEMPLATE GET --

    parser_template_get = template_subparsers.add_parser(
        'get',
        help='get template file from its id')
    parser_template_get.set_defaults(func=template_get)
    parser_template_get.add_argument(
        'name', type=str,
        help='identifier of the template')

    # PACKAGE ----------------------------------------------------------------
    parser_package = subparsers.add_parser('package', help='')
    package_subparsers = parser_package.add_subparsers(help='')

    parser_package_add = package_subparsers.add_parser('add', help='')
    parser_package_add.set_defaults(func=package_add)
    parser_package_add.add_argument('path', type=str, help='')

    parser_add = subparsers.add_parser('add', help="")
    parser_add.set_defaults(func=add)
    parser_add.add_argument("package", type=str, help="")
    parser_add.add_argument("asset", type=str, help="")
    parser_add.add_argument("template", type=str, help="")

    parser_fetch = subparsers.add_parser('fetch', help="")
    parser_fetch.set_defaults(func=fetch)
    parser_fetch.add_argument("package", type=str, help="")
    parser_fetch.add_argument("asset", type=str, help="")
    parser_fetch.add_argument("-b", "--branch", default=None, help="")
    parser_fetch.add_argument("-t", "--tag", default=None, help="")
    parser_fetch.add_argument("-c", "--commit", default=None, help="")
    parser_fetch.add_argument("-e", "--editable", action="store_true", help="")
    parser_fetch.add_argument("-r", "--reset", action="store_true", help="")

    parser_commit = subparsers.add_parser('commit', help="")
    parser_commit.set_defaults(func=commit)
    parser_commit.add_argument("file", type=str, help="")
    parser_commit.add_argument("-k", "--keep", action="store_true", help="")

    parser_branch = subparsers.add_parser('branch', help="")
    branch_subparsers = parser_branch.add_subparsers(help='')
    parser_branch_add = branch_subparsers.add_parser('add', help='')
    parser_branch_add.set_defaults(func=branch_add)
    parser_branch.add_argument("package_path", type=str, help="")
    parser_branch.add_argument("asset", type=str, help="")
    parser_branch.add_argument("branch_new", type=str, help="")
    parser_branch.add_argument("branch_parent", type=str, help="")

    parser_tag = subparsers.add_parser('tag', help="")
    tag_subparsers = parser_tag.add_subparsers(help='')
    parser_tag_add = tag_subparsers.add_parser('add', help='')
    parser_tag_add.set_defaults(func=tag_add)
    parser_tag.add_argument("package_path", type=str, help="")
    parser_tag.add_argument("asset", type=str, help="")
    parser_tag.add_argument("branch", type=str, help="")
    parser_tag.add_argument("tag", type=str, help="")

    return parser

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        s = args.func(args)
        if s: sys.exit(0)
        else: sys.exit(1)
    sys.exit(0)
