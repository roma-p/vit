import os
from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.connection.connection_utils import ssh_connect_auto
from vit.vit_lib import commit
from vit.custom_exceptions import VitCustomException, Asset_NotEditable_E
import logging
log = logging.getLogger("vit")


def _callback_commit(args):
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
                vit_connection, args.file, args.message,
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


def _create_parser_commit():
    parser = ArgumentParser('commit')
    parser.set_defaults(func=_callback_commit)
    parser.help = "commit changes done locally to an asset to origin repository."
    parser.description = """
--- vit COMMIT command ---

This command is to commit modification done for an asset on a given branch.

To use it, pass the path to the reference file of the branch on which you want to commit.
You also need to pass a commit message.
eg:
    vit commit dir/dir/file-branch-base.ma -m"I did things"

To commit an asset, you have to own the "editable" token for that specific branch.
Only one artist can have this token at once.
To get this token, either:
    - checkout the asset as editable: see help on 'vit checkout' cmd.
    - update the asset as editable: see help on 'vit update' cmd.

To prevent artists sleeping on editable assets, denying other artists to work on them,
by default, when commiting:
    - the editable token will be released.
    - the file reference will be deleted from your working copy.

- To keep the file as read-only, use '-k'
- To keep the file as editable, 'use '-K'
"""
    parser.epilog = """
examples:

-> commit the reference file and release editable token, del reference file.
    vit commit package1/asset_A.ma -m"I have finished working on this"
-> commit the reference file and keep it as 'editable'.
    vit commit package1/asset_A.ma -m"I have not finished here!" -K
"""
    parser.add_argument(
        "file", type=str,
        help="path of the file you want to commit."
    )
    parser.add_argument(
        "-k", "--keep_file", action="store_true",
        help="local file won't be deleted on commit. if the file was fetch as"
             "'editable', the 'editable' token WILL be released"
    )
    parser.add_argument(
        "-K", "--keep_editable", action="store_true",
        help="local file won't be deleted on commit. if the file was fetch as"
             "'editable', the 'editable' token WILL NOT be released"
    )
    parser.add_argument(
        "-m", "--message",
        help="commit message"
    )
    return parser


PARSER_WRAPPER_COMMIT = SubArgumentParserWrapper(
    arg_parser=_create_parser_commit(),
    origin_connection_needed=True
)
