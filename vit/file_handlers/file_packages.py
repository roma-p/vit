import os
import json

from vit import constants
from vit import py_helpers
from vit import path_helpers
from vit.file_handlers.json_file import JsonFile

class PackageIndex(JsonFile):

    def __init__(self, path):
        super().__init__(os.path.join(path,constants.VIT_DIR, constants.VIT_PACKAGES))

    @staticmethod
    def create_file(path):
        return py_helpers.create_empty_json(
            path_helpers.get_vit_file_config_path(
                path,
                constants.VIT_PACKAGES
            )
        )

    @JsonFile.file_read
    def set_package(self, package_path, package_tree_file_path):
        self.data[package_path] = package_tree_file_path

    @JsonFile.file_read
    def get_package_tree_file_path(self, package_path):
        return self.data.get(package_path, None)

    @JsonFile.file_read
    def list_packages(self):
        return tuple(self.data.keys())

    @JsonFile.file_read
    def check_package_exists(self, package_path):
        return package_path in self.data

