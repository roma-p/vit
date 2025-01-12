from vit.cli.argument_parser import ArgumentParser
from vit.cli.argument_parser import add_subparser_from_parser_wrapper

from vit.cli import (
    cli_add, cli_checkout, cli_list,
    cli_commit, cli_free, cli_branch,
    cli_infos, cli_log, cli_clean,
    cli_init, cli_clone, cli_package,
    cli_fetch, cli_tag,
)


def create_parser():

    # sub_command_table = (
    #     (   "template", cli_template.create_parser(),
    #         "manage asset templates."
    #     ),
    #     (   "rebase", cli_rebase.create_parser(),
    #         "will add a new commit on branch, identical to the one given."
    #     ),
    #     (   "update", cli_update.create_parser(),
    #         "update checkout file to latest commit of branch. also useful"
    #         " to make a checkout file editable."
    #     ),
    # )
    #

    sub_command_parser_wrapper = (
        cli_add.PARSER_WRAPPER_ADD,
        cli_branch.PARSER_WRAPPER_BRANCH,
        cli_checkout.PARSER_WRAPPER_CHECKOUT,
        cli_clean.PARSER_WRAPPER_CLEAN,
        cli_clone.PARSER_WRAPPER_CLONE,
        cli_commit.PARSER_WRAPPER_COMMIT,
        cli_fetch.PARSER_WRAPPER_FETCH,
        cli_free.PARSER_WRAPPER_FREE,
        cli_infos.PARSER_WRAPPER_INFO,
        cli_init.PARSER_WRAPPER_INIT,
        cli_list.PARSER_WRAPPER_LIST,
        cli_log.PARSER_WRAPPER_LOG,
        cli_package.PARSER_WRAPPER_PACKAGE,
        cli_tag.PARSER_WRAPPER_TAG,
    )

    parser = ArgumentParser(
        description='A VCS specialised for VFX data.'
    )
    subparser = parser.add_subparsers(help='main commands are:')
    for parserWrapper in sub_command_parser_wrapper:
        add_subparser_from_parser_wrapper(subparser, parserWrapper)

    return parser
