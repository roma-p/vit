import os
from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.connection.vit_connection import ssh_connect_auto
from vit.vit_lib import commit
from vit.custom_exceptions import VitCustomException, Asset_NotEditable_E

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def commit_func(args):
    if not args.message:
        log.error("No commit message specified")
        return False
    keep_file = args.keep_file or args.keep_editable
    keep_editable = args.keep_editable

    err = "Could not commit file {}".format(args.file)
    if not command_line_helpers.is_vit_repo():
        return False
    try:
        vit_connection = ssh_connect_auto(os.getcwd())
    except VitCustomException as e:
        log.error(err)
        log.error(str(e))
        return False, None
    try:
        with vit_connection:
            commit.commit_file(
                os.getcwd(), args.file, args.message,
                keep_file, keep_editable
            )
    except Asset_NotEditable_E as e:
        log.error(err)
        log.error(str(e))
        log.info("* you can try to fetch it as editable so you can commit it")
        log.info("    following line won't overwrite your local modification")
        log.info("    vit update {} -e".format(args.file))
        return False
    except VitCustomException as e:
        log.error(err)
        log.error(str(e))
        return False
    else:
        log.info("file {} successfully committed".format(args.file))
        return True


def create_parser():
    parser_commit = ArgumentParser('commit')
    parser_commit.set_defaults(func=commit_func)
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
    return parser_commit
