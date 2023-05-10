from vit.cli.argument_parser import ArgumentParser
from vit.cli import command_line_helpers
from vit.vit_lib import asset_template
import logging
log = logging.getLogger("vit")


def create_template(args):
    status, _ = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        asset_template.create_asset_template,
        "Could not create template {} from {}".format(args.template, args.file),
        args.template, args.file, args.force
    )
    if status:
        log.info("template {} successfully created from file {}".format(
            args.template,
            args.file))
    return status


def get_template(args):
    status, template_path_local = command_line_helpers.exec_vit_cmd_from_cwd_with_server(
        asset_template.get_template,
        "Could not get template file for {}".format(args.template),
        args.template
    )
    if status:
        log.info("template {} successfully copied at: {}".format(
            args.template,
            template_path_local
        ))
    return status


def list_templates(args):
    status, template_data = command_line_helpers.exec_vit_cmd_from_cwd_without_server(
        asset_template.list_templates,
        "Could not list templates."
    )
    if status:
        if not template_data:
            log.info("no template found on origin repository")
        else:
            log.info("templates found on origin repository are:")
            for template_id, template_file in template_data.items():
                log.info("    - {} : {}".format(template_id, template_file))
    return status


def create_parser():
    parser_template = ArgumentParser('template')
    template_subparsers = parser_template.add_subparsers(help='')
    
    # -- TEMPLATE ADD --
    parser_template_add = template_subparsers.add_parser(
        'add',
        help='add a new asset template to origin.'
    )
    parser_template_add.set_defaults(func=create_template)
    parser_template_add.add_argument(
        'template', type=str,
        help='identifier of the template. Template ids are unique.'
    )
    parser_template_add.add_argument(
        'file', type=str,
        help='path to the file to be used as asset template'
    )
    parser_template_add.add_argument(
        "-f", "--force",
        action="store_true",
        help="if template ids already exists, "
             "its template file will be overwritten"
    )

    # -- TEMPLATE GET --
    parser_template_get = template_subparsers.add_parser(
        'get',
        help='fetch template file locally from origin using its id')
    parser_template_get.set_defaults(func=get_template)
    parser_template_get.add_argument(
        'template', type=str,
        help='identifier of the template')
    
    # -- TEMPLATE LIST --
    parser_template_list = template_subparsers.add_parser(
        'list',
        help='list all templates found on origin repository.')
    parser_template_list.set_defaults(func=list_templates)

    return parser_template
