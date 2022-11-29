import shutil
import unittest

from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.vit_lib import (
    repo_init_clone,
    package, asset,
    asset_template,
    checkout, commit,
    clean
)

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

class TestClean(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_local_path_1 = "tests/local_repo1"
    test_local_path_2 = "tests/local_repo2"
    package_ok = "the/package"
    package_ko = "the/package/nupe"
    template_file_path = "tests/test_data/mod_template.ma"
    template_id = "mod"
    asset_ok = "asset_ok"
    asset_ko = "asset_ko"
    checkout_path_repo_1 = "tests/local_repo1/the/package/asset_ok-branch-base.ma"
    checkout_path_repo_2 = "tests/local_repo2/the/package/asset_ok-branch-base.ma"

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

    def test_clean_editable_file_commited_and_released(self):
        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
            editable=True
        )
        self._append_line_to_file(self.checkout_path_repo_1, "ouiii")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "new commit",
            keep_file=True,
            keep_editable=True
        )
        self.assertEqual(
            (checkout_file,),
            clean.get_files_to_clean(self.test_local_path_1)["editable"])
        commit.release_editable(self.test_local_path_1, checkout_file)
        self.assertEqual(
            (checkout_file,),
            clean.get_files_to_clean(self.test_local_path_1)["to_clean"])
        self._append_line_to_file(self.checkout_path_repo_1, "ouiii")
        self.assertEqual(
            (checkout_file,),
            clean.get_files_to_clean(self.test_local_path_1)["changes"])

    def test_read_only_file_then_cleaned(self):
        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
        )
        self.assertEqual(
            (checkout_file,),
            clean.get_files_to_clean(self.test_local_path_1)["to_clean"])
        clean.clean_files(self.test_local_path_1, checkout_file)
        self.assertFalse(os.path.exists(
            os.path.join(
                self.test_local_path_1,
                checkout_file
            )
        ))

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
