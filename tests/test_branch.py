import shutil
import unittest

from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.vit_lib import (
    repo_init_clone,
    package, asset,
    asset_template,
    branch, tag
)

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

class TestBranch(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_local_path_1 = "tests/local_repo1"
    test_local_path_2 = "tests/local_repo2"
    package_ok = "the/package"
    package_ko = "the/package/nupe"
    template_file_path = "tests/test_data/mod_template.ma"
    template_id = "mod"
    asset_ok = "asset_ok"
    asset_ko = "asset_ko"
    checkout_path_repo_1 = "tests/local_repo1/the/package/asset_ok-base.ma"
    checkout_path_repo_2 = "tests/local_repo2/the/package/asset_ok-base.ma"

    def setUp(self):
        VitConnection.SSHConnection = FakeSSHConnection
        self._clean_dir()
        self._init_repos()

    def tearDown(self):
        VitConnection.SSHConnection = SSHConnection
        self._clean_dir()

    def _init_repos(self):
        repo_init_clone.init_origin(self.test_origin_path_ok)
        repo_init_clone.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_1,
            "user1", "localhost"
        )
        repo_init_clone.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_2,
            "user2", "localhost"
        )
        asset_template.create_asset_template(
            self.test_local_path_1,
            self.template_id,
            self.template_file_path
        )
        package.create_package(
            self.test_local_path_1,
            self.package_ok,
            force_subtree=True
        )
        asset.create_asset_from_template(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            self.template_id
        )

    def test_create_branch(self):
        branch.create_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "new_branch",
            branch_parent="base",
        )
        self.assertSetEqual(
            {"base", "new_branch"},
            set(branch.list_branches(
                self.test_local_path_1,
                self.package_ok,
                self.asset_ok
            ))
        )

    def test_create_branch_from_another_branch_but_origin_branch_not_found(self):
        with self.assertRaises(Branch_NotFound_E):
            branch.create_branch(
                self.test_local_path_1,
                self.package_ok,
                self.asset_ok,
                "new_branch",
                branch_parent="branch_not_found",
            )

    def test_create_branch_from_another_branch_but_new_branch_already_exists(self):
        with self.assertRaises(Branch_AlreadyExist_E):
            branch.create_branch(
                self.test_local_path_1,
                self.package_ok,
                self.asset_ok,
                "base",
                branch_parent="base"
            )

    def test_create_branch_from_another_branch_and_create_tag(self):
        branch.create_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "new_base",

            branch_parent="base", 
            create_tag=True
        )
        self.assertTupleEqual(
            ('asset_ok-new_base-v0.1.0',),
            tag.list_tags(self.test_local_path_1, self.package_ok, self.asset_ok)
        )

    def _clean_dir(self):
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_1,
                self.test_local_path_2):
            self._rm_dir(path)

    @staticmethod
    def _rm_dir(directory):
        if os.path.exists(directory):
            shutil.rmtree(directory, ignore_errors=True)

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
