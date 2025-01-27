from vit import constants
from vit import py_helpers
from vit.path_helpers import localize_path
from vit.file_handlers.json_file import JsonFile


class IndexPackage(JsonFile):

    def __init__(self, local_path):
        super().__init__(local_path)

    @staticmethod
    def create_file(local_path):
        return py_helpers.create_empty_json(local_path)

    @staticmethod
    def get_local_index_package(local_path):
        return IndexPackage(localize_path(local_path, constants.VIT_PACKAGES))

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
