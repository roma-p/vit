from vit import py_helpers
from vit.file_handlers.json_file import JsonFile

import logging
log = logging.getLogger()

DEFAULT_BRANCH = "base"


class TreeAsset(JsonFile):

    @staticmethod
    def create_file(file_path, asset_name):
        data = {
            "asset_name": asset_name,
            "commits": {},
            "branches": {},
            "editors": {},
            "tags_light": {}
        }
        return py_helpers.write_json(file_path, data)

    def __init__(self, file_path):
        super().__init__(file_path)

    # Services to use within context manager ---------------------------------

    # -- base methods.

    @JsonFile.file_read
    def add_commit(self, filepath, parent, date, user, sha256, commit_mess):
        self.data["commits"].update({
            filepath: {
                "parent": parent,
                "date": date,
                "user": user,
                "sha256": sha256,
                "message": commit_mess,
            }
        })

    @JsonFile.file_read
    def set_branch(self, branch, filepath):
        self.data["branches"][branch] = filepath

    @JsonFile.file_read
    def list_branches(self):
        return self.data["branches"].keys()

    @JsonFile.file_read
    def add_tag_lightweight(self, filepath, tagname):
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
        for branch, f in self.data["branches"].items():
            if f == file:
                return branch
        return None

    # -- on event methods.

    @JsonFile.file_read
    def update_on_commit(
            self, filepath, new_filepath,
            parent, date, user, commit_mess,
            keep_editable=False):
        sha256 = py_helpers.calculate_file_sha(filepath)
        self.add_commit(new_filepath, parent, date, user, sha256, commit_mess)
        for branch, f in self.data["branches"].items():
            if f == parent:
                self.data["branches"][branch] = new_filepath
        if keep_editable:
            self.set_editor(new_filepath, user)
        self.remove_editor(parent)

    @JsonFile.file_read
    def create_new_branch_from_file(
            self, filepath,
            branch_parent,
            branch_new,
            date, user):
        if branch_new in self.data["branches"]:
            log.error("branches {} already exists".format(branch_parent))
            return False
        parent = self.data["branches"][branch_parent]
        sha256 = self.get_sha256(parent)
        self.add_commit(filepath, parent, date, user, sha256, "branch creation")
        self.set_branch(branch_new, filepath)
        return True

    @JsonFile.file_read
    def get_branch_current_file(self, branch):
        return self.data["branches"].get(branch, None)
