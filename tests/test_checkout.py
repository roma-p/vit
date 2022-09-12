import shutil
import unittest
import glob
from vit import py_helpers
from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.commands import (
    repo_init_clone,
    package, asset,
    asset_template,
    checkout
)

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

class TestCheckout(unittest.TestCase):

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

    def test_checkout(self):
        self.assertEqual(
            self.checkout_path_repo_1,
            checkout.checkout_asset_by_branch(
                self.test_local_path_1,
                self.package_ok,
                self.asset_ok,
                "base"
            )
        )
        self.assertTrue(os.path.exists(self.checkout_path_repo_1))
        self.assertEqual(
            self.checkout_path_repo_2,
            checkout.checkout_asset_by_branch(
                self.test_local_path_2,
                self.package_ok,
                self.asset_ok,
                "base"
            )
        )
        self.assertTrue(os.path.exists(self.checkout_path_repo_2))

    def test_checkout_package_not_found(self):
        with self.assertRaises(Package_NotFound_E):
            checkout.checkout_asset_by_branch(
                self.test_local_path_1,
                self.package_ko,
                self.asset_ok,
                "base"
            )

    def test_checkout_asset_not_found(self):
        with self.assertRaises(Asset_NotFound_E):
            checkout.checkout_asset_by_branch(
                self.test_local_path_1,
                self.package_ok,
                self.asset_ko,
                "base"
            )

    def test_checkout_branch_not_found(self):
        with self.assertRaises(Branch_NotFound_E):
            checkout.checkout_asset_by_branch(
                self.test_local_path_1,
                self.package_ok,
                self.asset_ok,
                "non_existing_branch"
            )

    def test_checkout_as_editable(self):
        checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
            editable=True
        )

    def test_checkout_as_editable_but_already_has_editor(self):
        checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
            editable=True
        )
        with self.assertRaises(Asset_AlreadyEdited_E):
            checkout.checkout_asset_by_branch(
                self.test_local_path_2,
                self.package_ok,
                self.asset_ok,
                "base",
                editable=True
            )

    def test_double_checkout_rebase(self):
        checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
        )
        sha = py_helpers.calculate_file_sha(self.checkout_path_repo_1)
        self._append_line_to_file(self.checkout_path_repo_1, "bla bla")
        checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
            rebase=True
        )
        self.assertEqual(
            sha,
            py_helpers.calculate_file_sha(self.checkout_path_repo_1)
        )

    def test_double_checkout_no_rebase(self):
        checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
        )
        self._append_line_to_file(self.checkout_path_repo_1, "bla bla")
        sha = py_helpers.calculate_file_sha(self.checkout_path_repo_1)
        checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
        )
        self.assertEqual(
            sha,
            py_helpers.calculate_file_sha(self.checkout_path_repo_1)
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
