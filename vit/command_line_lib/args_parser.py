import argparse

from vit.command_line_lib import command_line_helpers
from vit.command_line_lib import (
    cl_template, cl_add, cl_checkout, cl_list,
    cl_commit, cl_free, cl_rebase, cl_update,
    cl_branch, cl_tag, cl_infos, cl_log,
    cl_clean, cl_init, cl_clone, cl_package
)

def create_parser():

    parser = argparse.ArgumentParser(
        description='A VCS specialised for VFX data.'
    )
    subparsers = parser.add_subparsers(help='main commands are:')

    sub_command_table = (
        (   "init", cl_init.create_parser(),
            "initialize a new VIT repository."
        ),
        (   "clone", cl_clone.create_parser(),
            "clone a repository to current location."
        ),
        (   "package",  cl_package.create_parser(),
            "manage package of assets."
        ),
        (   "template", cl_template.create_parser(),
            "manage asset templates."
        ),
        (   "add", cl_add.create_parser(),
            "add a new asset to origin repository."
        ),
        (   "checkout", cl_checkout.create_parser(),
            "checkout an asset from origin to local repository."
        ),
        (   "list", cl_list.create_parser(),
            "list all assets found on origin repository for given package."
        ),
        (   "commit", cl_commit.create_parser(),
            "commit changes done locally to an asset to origin repository." 
            "By default: releases the 'editable' token and delete local."
        ),
        (   "free", cl_free.create_parser(),
            "if an asset was checkout as editable, free the 'editable' token"
            "so that someone else can checkout the asset as 'editable'"
        ),
        (   "rebase", cl_rebase.create_parser(),
            "will add a new commit on branch, identical to the one given."
        ),
        (   "update", cl_update.create_parser(),
            "update checkout file to latest commit of branch. also useful"
            " to make a checkout file editable."
        ),
        (   "branch", cl_branch.create_parser(),
            "manage branches of a given asset."
        ),
        (   "tag", cl_tag.create_parser(), "manage tags of a given asset"),
        (   "info", cl_infos.create_parser(),
            "get information on a ref file."
        ),
        (   "log", cl_log.create_parser(), "log historic of given asset."),
        (   "clean", cl_clean.create_parser(),
            "remove files on local repositary that can safely be removed."
        ),
    )

    for item in sub_command_table:
        command_name, argument_parser, help_str = item
        command_line_helpers.add_parser(
            subparsers, argument_parser,
            command_name, help=help_str
        )

    return parser
