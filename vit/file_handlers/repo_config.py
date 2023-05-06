import time
from vit import constants
from vit import py_helpers
from vit import path_helpers
from vit.file_handlers.json_file import JsonFile


class RepoConfig(JsonFile):

    def __init__(self, path):
        super().__init__(
            path_helpers.localize_path(path, constants.VIT_CONFIG)
        )

    @staticmethod
    def create(
            path,
            repository_format_version=0,
            origin=True,
            remote=False):
        py_helpers.write_json(
            path_helpers.localize_path(path, constants.VIT_CONFIG), {
                "core": {
                    "repository_format_version": repository_format_version,
                },
                "origin_config": {
                },
                "current_copy": {
                    "is_origin": origin,
                    "is_working_copy_remote": remote
                },
                "origin_link": {
                    "host": None,
                    "path": None,
                    "username": None,
                },
                "last_fetch_time": None
            }
        )

    @JsonFile.file_read
    def edit_on_clone(self, origin_host, origin_path, username):
        updated_data = {
            "origin_config": {
            },
            "current_copy": {
                "is_origin": False
            },
            "origin_link": {
                "host": origin_host,
                "path": origin_path,
                "username": username
            },
            "last_fetch_time": time.time()
        }
        self.data.update(**updated_data)

    @JsonFile.file_read
    def get_origin_ssh_info(self):
        config_data = self.data["origin_link"]
        return config_data["host"], config_data["path"], config_data["username"]

    @JsonFile.file_read
    def get_last_fetch_time(self):
        return self.data["last_fetch_time"]

    @JsonFile.file_read
    def update_last_fetch_time(self):
        self.data["last_fetch_time"] = time.time()


def get_origin_ssh_info(path):
    with RepoConfig(path) as repo_config:
        ret = repo_config.get_origin_ssh_info()
    return ret
