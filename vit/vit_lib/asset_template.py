import os
from vit import constants
from vit import py_helpers
from vit.custom_exceptions import *
from vit.path_helpers import localize_path
from vit.file_handlers.index_template import IndexTemplate


def create_asset_template(
        vit_connection, template_id,
        template_filepath, force=False):

    if not os.path.exists(template_filepath):
        raise Path_FileNotFound_E(template_filepath)

    vit_connection.get_metadata_from_origin(constants.VIT_TEMPLATE_CONFIG)

    with IndexTemplate(vit_connection.local_path) as index_template:

        if not force and not index_template.is_template_id_free(template_id):
            raise Template_AlreadyExists_E(template_id)

        template_scn_dst = os.path.join(
            constants.VIT_TEMPLATE_DIR,
            os.path.basename(template_filepath)
        )

        index_template.reference_new_template(
            template_id,
            template_scn_dst,
            py_helpers.calculate_file_sha(template_filepath)
        )

    vit_connection.put_vit_file(constants.VIT_TEMPLATE_CONFIG)
    vit_connection.put(template_filepath, template_scn_dst)


def get_template(vit_connection, template_id):
    vit_connection.get_metadata_from_origin(constants.VIT_TEMPLATE_CONFIG)

    with IndexTemplate(vit_connection.local_path) as index_template:
        template_data = index_template.get_template_path_from_id(template_id)
        if not template_data:
            raise Template_NotFound_E(template_id)

    template_path_origin, sha256 = template_data
    template_path_local = os.path.basename(template_path_origin)

    vit_connection.get_data_from_origin(
        template_path_origin,
        template_path_local,
        is_editable=True
    )
    return localize_path(vit_connection.local_path, template_path_local)


def list_templates(path):
    with IndexTemplate(path) as index_template:
        template_data = index_template.get_template_data()
    return template_data
