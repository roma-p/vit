from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.vit_lib import fetch

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def _callback_fetch(args):
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        fetch.fetch,
        "Could not ....",
    )
    if status:
        log.info("local repository metadata successfully updated!")
    return status


def _create_parser_fetch():
    parser = ArgumentParser('fetch')
    parser.set_defaults(func=_callback_fetch)
    parser.help = "update local metadata by fetching them from origin repositary."
    parser.description = """
--- vit FETCH command ---

This command is to update metadata with the one on origin repository.
Useful for all commands that don't connect to origin to do their process
eg: listing packages / branchs/ assets, log, graph...

"""
    return parser


PARSER_WRAPPER_FETCH = SubArgumentParserWrapper(
    arg_parser=_create_parser_fetch(),
    origin_connection_needed=True
)
