from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
import os
from vit.cli import command_line_helpers
from vit.vit_lib import clean

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def _callback_clean(args):
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


def _create_parser_clean():
    parser_clean = ArgumentParser('clean')
    parser_clean.set_defaults(func=_callback_clean)
    return parser_clean


PARSER_WRAPPER_CLEAN = SubArgumentParserWrapper(
    sub_command_name="clean",
    arg_parser=_create_parser_clean(),
    help="remove files on local repositary that can safely be removed.",
    description="""
--- vit CLEAN command ---

This command will remove all unused files from your local working copy.
Following types of files won't be cleaned:
    - all files checkout as 'editable' (see help on 'vit checkout' cmd)
    - all read only files that either:
        - have been modified locally (you may want to commit them later)
        - files that are dependancy of other asset checkout as editable.
    - untracked files: files on your working copy that don't belong to repository.
Other files (ready only + unchanged + not a dependancy) will be deleted.
""",
    epilog="",
    origin_connection_needed=True
)
