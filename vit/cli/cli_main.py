from vit.cli.argument_parser import ArgumentParser

from vit.cli import command_line_helpers
from vit.cli import (
    cli_template, cli_add, cli_checkout, cli_list,
    cli_commit, cli_free, cli_rebase, cli_update,
    cli_branch, cli_tag, cli_infos, cli_log,
    cli_clean, cli_init, cli_clone, cli_package,
    cli_fetch
)


def create_parser():

    parser = ArgumentParser(
        description='A VCS specialised for VFX data.'
    )
    subparser = parser.add_subparsers(help='main commands are:')

    sub_command_table = (
        (   "init", cli_init.create_parser(),
            "initialize a new VIT repository."
        ),
        (   "clone", cli_clone.create_parser(),
            "clone a repository to current location."
        ),
        (   "package",  cli_package.create_parser(),
            "manage package of assets."
        ),
        (   "template", cli_template.create_parser(),
            "manage asset templates."
        ),
        (   "add", cli_add.create_parser(),
            "add a new asset to origin repository."
        ),
        (   "checkout", cli_checkout._create_parser_checkout(),
            "checkout an asset from origin to local repository."
        ),
        (   "list", cli_list.create_parser(),
            "list all assets found on origin repository for given package."
        ),
        (   "commit", cli_commit.create_parser(),
            "commit changes done locally to an asset to origin repository." 
            "By default: releases the 'editable' token and delete local."
        ),
        (   "free", cli_free.create_parser(),
            "if an asset was checkout as editable, free the 'editable' token"
            "so that someone else can checkout the asset as 'editable'"
        ),
        (   "rebase", cli_rebase.create_parser(),
            "will add a new commit on branch, identical to the one given."
        ),
        (   "update", cli_update.create_parser(),
            "update checkout file to latest commit of branch. also useful"
            " to make a checkout file editable."
        ),
        (   "branch", cli_branch.create_parser(),
            "manage branches of a given asset."
        ),
        (   "tag", cli_tag.create_parser(), "manage tags of a given asset"),
        (   "info", cli_infos.create_parser(),
            "get information on a ref file."
        ),
        (   "log", cli_log.create_parser(), "log historic of given asset."),
        (   "clean", cli_clean.create_parser(),
            "remove files on local repositary that can safely be removed."
        ),
        (   "fetch", cli_fetch.create_parser(),
            "update local metadata by fetching them from origin repositary."
        ),
    )

    for item in sub_command_table:
        command_name, argument_parser, help_str = item
        subparser.add_existing_parser(
            argument_parser,
            command_name,
            help=help_str
        )

    return parser
