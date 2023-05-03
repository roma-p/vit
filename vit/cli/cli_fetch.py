from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.vit_lib import fetch

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def fetch_func(args):
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        fetch.fetch,
        "Could not ....",
    )
    if status:
        log.info("local repository metadata successfully updated!")
    return status


def create_parser():
    parser_fetch = ArgumentParser('fetch')
    parser_fetch.set_defaults(func=fetch_func)
    return parser_fetch
