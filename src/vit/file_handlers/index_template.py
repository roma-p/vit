import os

from vit import constants
from vit import py_helpers
from vit.path_helpers import localize_path
from vit.file_handlers.json_file import JsonFile


class IndexTemplate(JsonFile):

    @staticmethod
    def create_file(path):
        return py_helpers.create_empty_json(path)

    @staticmethod
    def get_index_template(local_path):
        return IndexTemplate(localize_path(
            local_path,
            constants.VIT_TEMPLATE_CONFIG)
        )

    def __init__(self, path):
        super().__init__(path)

    @JsonFile.file_read
    def reference_new_template(self, template_id, template_filepath, sha256):
        self.data[template_id] = [template_filepath, sha256]

    @JsonFile.file_read
    def get_template_path_from_id(self, template_id):
        return self.data.get(template_id, None)

    @JsonFile.file_read
    def is_template_id_free(self, template_id):
        return not bool(self.get_template_path_from_id(template_id))

    @JsonFile.file_read
    def get_template_data(self):
        return {
            template_id: os.path.basename(template_data[0])
            for template_id, template_data in self.data.items()
        }
