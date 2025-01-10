import os
from collections import defaultdict

from vit import constants
from vit import py_helpers
from vit import path_helpers
from vit.file_handlers.json_file import JsonFile

cfg_file_path = os.path.join(constants.VIT_DIR, constants.VIT_TRACK_FILE)


class IndexTrackedFile(JsonFile):

    @staticmethod
    def create_file(path):
        return py_helpers.create_empty_json(
            path_helpers.get_vit_repo_config_path(path,
                                                  constants.VIT_TRACK_FILE),
        )

    def __init__(self, path):
        super().__init__(os.path.join(path, cfg_file_path))

    @JsonFile.file_read
    def add_tracked_file(
            self, package_path,
            asset_name,
            filepath,
            checkout_type,
            checkout_value,
            origin_file_name=None,
            sha256=None):

        self.data[filepath] = {
            "sha256": sha256,
            "package_path": package_path,
            "asset_name": asset_name,
            "origin_file_name": origin_file_name,
            "checkout_type": checkout_type,
            "checkout_value": checkout_value,
        }

    @JsonFile.file_read
    def get_files_data(self, path):
        ret = {}
        for file_path, data_in in self.data.items():
            ret[file_path] = {
                "package_path":     data_in["package_path"],
                "asset_name":       data_in["asset_name"],
                "origin_file_name": data_in["origin_file_name"],
                "checkout_type":    data_in["checkout_type"],
                "checkout_value":   data_in["checkout_value"],
                "changes": not _is_same_sha(
                    os.path.join(path, file_path),
                    data_in["sha256"]
                )
            }
        return ret

    @JsonFile.file_read
    def gen_status_local_data(self, path):
        nested_dict = lambda: defaultdict(nested_dict)
        ret = nested_dict()

        for file_path, (stored_sha, package_path, asset_name, _ ) in self.data.items():
            modification_to_commit = not _is_same_sha(
                os.path.join(path, file_path),
                stored_sha
            )
            # FIXME ! get branch another way.......;
            ret[package_path][asset_name]["branch"] = {
                "file": file_path,
                "to_commit": modification_to_commit
            }
        return ret

    @JsonFile.file_read
    def clean(self):
        self.data = {}

    @JsonFile.file_read
    def remove_file(self, file_path):
        if file_path not in self.data:
            return
        self.data.pop(file_path, None)

    @JsonFile.file_read
    def set_new_original_file(self, checkout_path, new_original_file):
        data = self.data.get(checkout_path, None)
        if not data:
            return False
        data["origin_file_name"] = new_original_file
        return True

    @JsonFile.file_read
    def update_sha(self, checkout_path, sha256):
        if not self.data.get(checkout_path, None):
            return False
        self.data[checkout_path]["sha256"] = sha256
        return True

def _is_same_sha(file_complete_path, current_sha):
    if not current_sha:
        return False
    return current_sha == py_helpers.calculate_file_sha(file_complete_path)
