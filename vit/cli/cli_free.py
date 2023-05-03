from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.vit_lib import commit

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def free(args):
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        commit.release_editable,
        "Could not release file {} from beeing editable.".format(args.file),
        args.file
    )
    if status:
        log.info("file {} successfully freed, now can be checkout as editable.".format(args.file))
    return status


def create_parser():
    parser_free = ArgumentParser('free')
    parser_free.set_defaults(func=free)
    parser_free.add_argument(
        "file", type=str,
        help="path of the file you want to free."
    )
    return parser_free
