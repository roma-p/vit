import os
import json

import logging
log = logging.getLogger()

import time
from vit import constants
from vit import py_helpers
from vit.custom_exceptions import Asset_NotFound_E

DEFAULT_BRANCH = "base"

class AssetTreeFile(object):

    def __init__(self, path, package_path, asset_name):
        self.path = path
        self.package_path = package_path
        self.asset_name = asset_name

        self.asset_tree_file_path = self.get_asset_file_tree_path()

        self.file = None
        self.data = None

    def create_asset_tree_file(self, asset_filename, user, sha256):
        tree_dir_path = os.path.dirname(self.asset_tree_file_path)
        file_path = self.get_asset_file_path_from_filename(asset_filename)

        if not os.path.exists(tree_dir_path):
            os.makedirs(tree_dir_path)

        with open(self.get_asset_file_tree_path(), "a+") as f:
            self.file = f
            self.data = {
                "commits" : {},
                "branchs" : {},
                "editors": {},
                "tags_light": {}
            }

            self.add_commit(file_path, None, time.time(), user, sha256)
            self.set_branch(DEFAULT_BRANCH, file_path)
            json.dump(self.data, self.file, indent=4)


    # Handling context manager -----------------------------------------------

    def open_file(self):
        if not self.get_asset_file_tree_path():
            raise Asset_NotFound_E(self.package_path, self.asset_name)

        self.file = open(self.get_asset_file_tree_path(), "r+")
        self.data = json.load(self.file)

    def write_and_close_file(self):
        self.file.seek(0)
        json.dump(self.data, self.file, indent=4)
        self.file.truncate()
        self.file.close()
        self.data = None
        self.file = None

    def __enter__(self):
        self.open_file()
        return self

    def __exit__(self, type, value, traceback):
        self.write_and_close_file()

    def file_opened(func):
        def wrapper(self, *args, **kargs):
            if not self.file:
                log.error("file not open, can't access its data.")
                return
            return func(self, *args, **kargs)
        return wrapper

    # Services to use within context manager ---------------------------------

    # -- base methods.

    @file_opened
    def add_commit(self, filepath, parent, date, user, sha256):
        self.data["commits"].update({
            filepath : {
                "parent": parent,
                "date": date,
                "user": user,
                "sha256": sha256,
            }
        })

    @file_opened
    def set_branch(self, branch, filepath):
        self.data["branchs"][branch] = filepath

    @file_opened
    def add_tag_lightweight(self, filepath, tagname):
#       FIXME: handle this case in main_commands with an exception.
#        if not self.check_is_file_referenced_in_commits(filepath):
#            return False
        self.data["tags_light"][tagname] = filepath

    @file_opened
    def get_tag(self, tagname):
        return self.data["tags_light"].get(tagname, None)

    @file_opened
    def get_editor(self, filepath):
        return self.data["editors"].get(filepath, None)

    @file_opened
    def set_editor(self, filepath, user):
        self.data["editors"][filepath] = user

    @file_opened
    def remove_editor(self, filepath):
        if filepath in self.data["editors"]:
            self.data["editors"].pop(filepath)

    @file_opened
    def get_sha256(self, filepath):
        return self.data["commits"][filepath]["sha256"]

    @file_opened
    def check_is_file_referenced_in_commits(self, filepath):
        return filepath in self.data["commits"]

    @file_opened
    def get_branch_from_file(self, file):
        for branch, f in self.data["branchs"].items():
            if f == file:
                return branch
        return branch

    # -- on event methods.

    @file_opened
    def update_on_commit(self, filepath, new_filepath, parent, date, user, keep=False):
        sha256 = py_helpers.calculate_file_sha(os.path.join(self.path, filepath))
        self.add_commit(new_filepath, parent, date, user, sha256)
        for branch, f in self.data["branchs"].items():
            if f == parent:
                self.data["branchs"][branch] = new_filepath
        if keep:
            self.set_editor(new_filepath, user)
        self.remove_editor(parent)

    @file_opened
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

    @file_opened
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

