from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
import os
from vit.cli import command_line_helpers
from vit.vit_lib import clean
from vit.cli import logger


def _callback_clean(args):
    status, files_dict = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        clean.get_files_to_clean, "Could not get files to clean"
    )
    if status:
        def print_file(f, tab_number=1):
            logger.log.info("\t"*tab_number+"- {}".format(f))

        if not files_dict["to_clean"]:
            logger.log.info("no file to clean")
        else:
            logger.log.info("following files will be cleaned:")
            for f in files_dict["to_clean"]:
                print_file(f)
        if files_dict["editable"] or files_dict["changes"]:
            logger.log.info("following files won't be cleaned:")
            if files_dict["editable"]:
                logger.log.info("\tfiles checkout as editable:")
                for f in files_dict["editable"]:
                    print_file(f, 2)
            if files_dict["changes"]:
                logger.log.info("\tuncommit changes on files:")
                for f in files_dict["changes"]:
                    print_file(f, 2)
        clean.clean_files(os.getcwd(), *files_dict["to_clean"])
    return status


def _create_parser_clean():
    parser = ArgumentParser('clean')
    parser.set_defaults(func=_callback_clean)
    parser.help = "remove files on local repositary that can safely be removed."
    parser.description = """
--- vit CLEAN command ---

This command will remove all unused files from your local working copy.
Following types of files won't be cleaned:
    - all files checkout as 'editable' (see help on 'vit checkout' cmd)
    - all read only files that either:
        - have been modified locally (you may want to commit them later)
        - files that are dependancy of other asset checkout as editable.
    - untracked files: files on your working copy that don't belong to repository.
Other files (ready only + unchanged + not a dependancy) will be deleted.
"""
    return parser


PARSER_WRAPPER_CLEAN = SubArgumentParserWrapper(
    arg_parser=_create_parser_clean(),
    origin_connection_needed=True
)
