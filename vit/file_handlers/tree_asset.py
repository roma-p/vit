import os
import json

import logging
log = logging.getLogger()

import time
from vit import constants
from vit import py_helpers
from vit.custom_exceptions import Asset_NotFound_E

from vit.file_handlers.json_file import JsonFile

DEFAULT_BRANCH = "base"

class TreeAsset(JsonFile):

    @staticmethod
    def create_file(file_path, asset_name, **kargs):
        data = {
            "commits" : {},
            "branchs" : {},
            "editors": {},
            "tags_light": {}
        }
        return py_helpers.write_json(file_path, data)

    def __init__(self, file_path):
        super().__init__(file_path)

    # Services to use within context manager ---------------------------------

    # -- base methods.

    @JsonFile.file_read
    def add_commit(self, filepath, parent, date, user, sha256):
        self.data["commits"].update({
            filepath : {
                "parent": parent,
                "date": date,
                "user": user,
                "sha256": sha256,
            }
        })

    @JsonFile.file_read
    def set_branch(self, branch, filepath):
        self.data["branchs"][branch] = filepath

    @JsonFile.file_read
    def list_branchs(self):
        return self.data["branchs"].keys()

    @JsonFile.file_read
    def add_tag_lightweight(self, filepath, tagname):
#       FIXME: handle this case in main_commands with an exception.
#        if not self.check_is_file_referenced_in_commits(filepath):
#            return False
        self.data["tags_light"][tagname] = filepath

    @JsonFile.file_read
    def get_tag(self, tagname):
        return self.data["tags_light"].get(tagname, None)

    @JsonFile.file_read
    def list_tags(self):
        return self.data["tags_light"].keys()

    @JsonFile.file_read
    def get_editor(self, filepath):
        return self.data["editors"].get(filepath, None)

    @JsonFile.file_read
    def set_editor(self, filepath, user):
        self.data["editors"][filepath] = user

    @JsonFile.file_read
    def remove_editor(self, filepath):
        if filepath in self.data["editors"]:
            self.data["editors"].pop(filepath)

    @JsonFile.file_read
    def get_sha256(self, filepath):
        return self.data["commits"][filepath]["sha256"]

    @JsonFile.file_read
    def check_is_file_referenced_in_commits(self, filepath):
        return filepath in self.data["commits"]

    @JsonFile.file_read
    def get_branch_from_file(self, file):
        for branch, f in self.data["branchs"].items():
            if f == file:
                return branch
        return branch

    # -- on event methods.

    @JsonFile.file_read
    def update_on_commit(self, filepath, new_filepath, parent, date, user, keep=False):
        sha256 = py_helpers.calculate_file_sha(filepath)
        self.add_commit(new_filepath, parent, date, user, sha256)
        for branch, f in self.data["branchs"].items():
            if f == parent:
                self.data["branchs"][branch] = new_filepath
        if keep:
            self.set_editor(new_filepath, user)
        self.remove_editor(parent)

    @JsonFile.file_read
    def create_new_branch_from_file(
            self, filepath,
            branch_parent,
            branch_new,
            date, user):
        if branch_new in self.data["branchs"]:
            log.error("branches {} already exists".format(branch_parent))
            return False
        parent = self.data["branchs"][branch_parent]
        sha256 = self.get_sha256(parent)
        self.add_commit(filepath, parent, date, user, sha256)
        self.set_branch(branch_new, filepath)
        return True

#FIXME: branch not found error here.
#FIXME: lots of error to handle here: package_not_found or reference / asset_not_found.
#FIXME: branchs already exists.
# OR MAYBE NOT? MAYBE PUT THE LOGIC IN MAIN COMMANDS?

    @JsonFile.file_read
    def get_branch_current_file(self, branch):
        return self.data["branchs"].get(branch, None)

    # Private  ---------------------------------------------------------------

    def get_asset_file_path_from_filename(self, asset_filename):
        return os.path.join(
            self.package_path,
            self.asset_name,
            asset_filename
        )

    def get_asset_file_tree_path(self):
         return os.path.join(
            self.path,
            constants.VIT_DIR,
            constants.VIT_ASSET_TREE_DIR,
            self._gen_package_dir_name(),
            "{}.json".format(self.asset_name)
        )

    def get_package_file_tree_path(self):
        return os.path.join(
            self.path,
            constants.VIT_DIR,
            constants.VIT_ASSET_TREE_DIR,
            self._gen_package_dir_name()
        )

    def _gen_package_dir_name(self):
        return self.package_path.replace("/", "-")
