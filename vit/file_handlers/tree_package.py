import time
from vit import py_helpers
from vit.file_handlers.json_file import JsonFile


class TreePackage(JsonFile):

    @staticmethod
    def create_file(file_path, package_name):
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
        return tuple(self.data["assets"].keys())

    @JsonFile.file_read
    def get_asset_tree_file_path(self, asset_name):
        return self.data["assets"].get(asset_name, None)

    @JsonFile.file_read
    def set_asset(self, asset_name, asset_tree_file_path):
        self.data["assets"][asset_name] = asset_tree_file_path
