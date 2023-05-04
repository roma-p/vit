import time
from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.vit_lib import infos

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def _callback_infos(args):
    if args.file is not None:
        return _print_single_files(args)
    else:
        return _print_all_files(args)


def _print_single_files(args):
    status, data = command_line_helpers.execute_vit_command(
        infos.get_info_from_ref_file,
        "Could not get info for file: {}".format(args.file),
        args.file
    )
    if status:
        formatted_time = time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.localtime(data["last_fetch"]))
        print("last fetch: {}".format(formatted_time))
        print(args.file)
        print("{}, {} -> {}".format(
            data["asset_name"],
            data["checkout_type"],
            data["checkout_value"]
        ))
        print("package: {}".format(data["package_path"]))
        print(" - editable: {}".format(data["editable"]))
        print(" - changes: {}".format(data["changes"]))
    return status


def _print_all_files(args):
    status, data = command_line_helpers.execute_vit_command(
        infos.get_info_from_all_ref_files,
        "Could not get infos on local files: "
    )
    if status:
        formatted_time = time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.localtime(data["last_fetch"]))
        print("last fetch: {}".format(formatted_time))
        if data["editable"]:
            print("")
            print("editable files:")
            _print_info_ref_files(data["editable"])
        if data["readonly"]:
            print("")
            print("read only files:")
            _print_info_ref_files(data["readonly"])
    return status


def _print_info_ref_files(data):
    print("")
    for package, package_data in data.items():
        print("- "+package)
        for asset, asset_data in package_data.items():
            print("\t- "+asset)
            for file, file_data in asset_data.items():
                _print_info_single_ref_files(file, file_data)


def _print_info_single_ref_files(file_path, data):
    print("\t\t-> "+file_path)
    print("\t\t\t{} -> {} ".format(data["checkout_type"], data["checkout_value"]))
    changes_str = "Yes" if data["changes"] else "No"
    print("\t\t\tchanges -> {}.".format(changes_str))


def _create_parser_info():
    parser = ArgumentParser('info')
    parser.set_defaults(func=_callback_infos)
    parser.help = "commit changes done locally to an asset to origin repository."
    parser.description = """
--- vit INFO command ---

This command will print infos on the state of your local copy. 
It will tell you
- which file reference correspond to which package / asset / branch etc...
- which file has the editable token
- which file has been modified since your last commit

You can use "-f" file to get information on a single reference file.
"""
    parser.add_argument(
        "-f", "--file", default=None, type=str,
        help="path to the file to get info from.")
    return parser


PARSER_WRAPPER_INFO = SubArgumentParserWrapper(
    arg_parser=_create_parser_info(),
    may_not_be_up_to_date=True
)
