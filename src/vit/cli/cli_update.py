from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.vit_lib import update
from vit.cli import logger


def update_func(args):
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        update.update,
        "Could not update file {}".format(args.file),
        args.file, args.editable, args.reset
    )
    if status:
        logger.log.info("{} successfully updated".format(args.file))
    return status


def create_parser():
    parser_update = ArgumentParser('update')
    parser_update.set_defaults(func=update_func)
    parser_update.add_argument(
        "file", type=str,
        help="path of the file you want to update."
    )
    parser_update.add_argument(
        "-e", "--editable", action="store_true",
        help="checkout the asset as 'editable': user will be the only one"
             " able to commit. Only works when fetching by branch."
    )
    parser_update.add_argument(
        "-r", "--reset", action="store_true",
        help="will discard and overwrite any change done locally to the asset."
    )
    return parser_update
