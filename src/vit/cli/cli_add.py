from vit.cli.argument_parser import ArgumentParser, SubArgumentParserWrapper
from vit.cli import command_line_helpers
from vit.vit_lib import asset
from vit.cli import logger



def _create_asset_from_template(package, asset_name, template):

    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        asset.create_asset_from_template,
        "Could not create asset {}".format(asset_name),
        package, asset_name, template
    )
    if status:
        logger.log.info("Asset {} successfully created at {}".format(
            asset_name, package)
        )
    return status


def _create_asset_from_file(package, asset_name, file):

    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        asset.create_asset_from_file,
        "Could not create asset {}".format(asset_name),
        package, asset_name, file
    )
    if status:
        logger.log.info("Asset {} successfully created at {}".format(
            asset_name, package)
        )
    return status


def _callback_add(args):
    if args.template:
        return _create_asset_from_template(
            args.package,
            args.asset,
            args.template
        )
    elif args.file:
        return _create_asset_from_file(
            args.package,
            args.asset,
            args.file
        )
    else:
        logger.log.info("Missing argument: either --template or --file")
        return False


def _create_parser_add():
    parser = ArgumentParser('add')
    parser.set_defaults(func=_callback_add)
    parser.description = """
--- vit ADD command ---

This command will add a new asset to origin repository.

It will not checkout the asset on current local repository,
it has to be done manually, see help on 'vit checkout' cmd.

An asset is any piece of data you want to versionnized:
asset / scene / cache / directory of images etc...

An asset is either create from :
- a template: '-t', for more en template see help on vit template.
- a file: '-f', just path the path to the file you want to versionnized.
- a directory: '-d': same as file but with entire repository.

An asset has to be contained in a package. For more on package see help on "vit package" cmd.

Asset name has to be unique within a package.

Upon creation, asset will be created with default "base" branch
    """
    parser.epilog = """
examples:

    vit my_package new asset -t empty_maya_scene
    vit my_package new asset -f ../../scene.usd
    """
    parser.add_argument(
        "package", type=str,
        help="path of the package in which to add asset.")
    parser.add_argument(
        "asset", type=str,
        help="id of the asset. Asset's ids have to be unique by package.")
    parser.add_argument(
        "-t", "--template", type=str,
        help="id of the template from which to create the asset.")
    parser.add_argument(
        "-f", "--file", type=str,
        help="path to the file from which create asset from.")
    return parser


# TODO: sub_command_name / help / description / epilog in ArguemntParser
# Wrapper: argParser / connection needed / may not be up to date.

PARSER_WRAPPER_ADD = SubArgumentParserWrapper(
    arg_parser=_create_parser_add(),
    origin_connection_needed=True
)
