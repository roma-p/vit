import argparse
from vit.command_line_lib import command_line_helpers
from vit.vit_lib import infos

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def infos_func(args):
    if args.file is not None:
        return print_single_files(args)
    else:
        return print_all_files(args)

def print_single_files(args):
    status, data = command_line_helpers.execute_vit_command(
        infos.get_info_from_ref_file,
        "Could not get info for file: ".format(args.file),
        args.file
    )
    if status:
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


def print_all_files(args):
    status, data = command_line_helpers.execute_vit_command(
        infos.get_info_from_all_ref_files,
        "Could not get infos on local files: "
    )
    if status:
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

def create_parser():
    parser_info = argparse.ArgumentParser('info')
    parser_info.set_defaults(func=infos_func)
    parser_info.add_argument(
        "-f", "--file", default=None, type=str,
        help="path to the file to get info from.")
    return parser_info
