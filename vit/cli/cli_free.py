from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.vit_lib import commit
import logging
log = logging.getLogger("vit")


def free(args):
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        commit.release_editable,
        "Could not release file {} from beeing editable.".format(args.file),
        args.file
    )
    if status:
        log.info("file {} successfully freed, now can be checkout as editable.".format(args.file))
    return status


def _create_parser_free():
    parser = ArgumentParser('free')
    parser.set_defaults(func=free)
    parser.help = "Release editable token from an asset"
    parser.description = """
--- vit FREE command ---

This command will release the editable token from a reference file.
For more on infos on editable token see help on 'vit checkout' cmd.
    """
    parser.add_argument(
        "file", type=str,
        help="path of the file you want to free."
    )
    return parser


PARSER_WRAPPER_FREE = SubArgumentParserWrapper(
    arg_parser=_create_parser_free(),
    origin_connection_needed=True
)
