from vit.cli.argument_parser import ArgumentParser
import os
from vit.cli import command_line_helpers
from vit.vit_lib import clean

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def clean_func(args):
    status, files_dict = command_line_helpers.execute_vit_command(
        clean.get_files_to_clean, "Could not get files to clean"
    )
    if status:
        def print_file(f, tab_number=1):
            log.info("\t"*tab_number+"- {}".format(f))

        if not files_dict["to_clean"]:
            log.info("no file to clean")
        else:
            log.info("following files will be cleaned:")
            for f in files_dict["to_clean"]:
                print_file(f)
        if files_dict["editable"] or files_dict["changes"]:
            log.info("following files won't be cleaned:")
            if files_dict["editable"]:
                log.info("\tfiles checkout as editable:")
                for f in files_dict["editable"]:
                    print_file(f, 2)
            if files_dict["changes"]:
                log.info("\tuncommit changes on files:")
                for f in files_dict["changes"]:
                    print_file(f, 2)
        clean.clean_files(os.getcwd(), *files_dict["to_clean"])
    return status    


def create_parser():
    parser_clean = ArgumentParser('clean')
    parser_clean.set_defaults(func=clean_func)
    return parser_clean
