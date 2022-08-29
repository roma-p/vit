import os
import time
from vit import constants
from vit import py_helpers
from vit import path_helpers
from vit.json_file import JsonFile

class FilePackageTree(JsonFile):

    @staticmethod
    def create_file(file_path, package_name, **kargs):
        data = {
            "package_name": package_name,
            "date": time.time(),
            "assets": {}
        }
        return py_helpers.write_json(file_path, data)

    def __init__(self, file_path):
        super().__init__(file_path)

    @JsonFile.file_read
    def has_asset(self, asset_name):
        return asset_name in self.data["assets"]

    @JsonFile.file_read
    def list_assets(self):
        return self.data["assets"].keys()

    @JsonFile.file_read
    def get_asset_tree_file_path(self, asset_name):
        return self.data["assets"].get(asset_name, None)

    @JsonFile.file_read
    def set_asset(self, asset_name, asset_tree_file_path):
        self.data["assets"][asset_name] = asset_tree_file_path
