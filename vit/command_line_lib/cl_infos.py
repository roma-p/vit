import argparse
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import infos

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def infos_func(args):
    status, data = command_line_helpers.execute_vit_command(
        infos.get_info_from_ref_file,
        "Could not get info for file: ".format(args.file),
        args.file
    )
    if status:
        log.info(args.file)
        log.info("{}, {} -> {}".format(
            data["asset_name"],
            data["checkout_type"],
            data["checkout_value"]
        ))
        log.info("package: {}".format(data["package_path"]))
        log.info(" - editable: {}".format(data["editable"]))
        log.info(" - changes: {}".format(data["changes"]))
    return status


def create_parser():
    parser_info = argparse.ArgumentParser('info')
    parser_info.set_defaults(func=infos_func)
    parser_info.add_argument(
        "file", type=str,
        help="path to the file to get info from.")
    return parser_info
