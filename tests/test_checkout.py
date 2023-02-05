import os
import shutil
import unittest

from vit import py_helpers
from vit.custom_exceptions import *
from vit.vit_lib import (
    checkout, tag,
    commit, fetch
)
from tests import vit_test_repo as repo
from vit.connection.vit_connection import ssh_connect_auto


class TestCheckout(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_checkout_by_branch(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            self.assertEqual(
                "the/package/asset_ok-branch-base.ma",
                checkout.checkout_asset_by_branch(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base"
                )
            )
        self.assertTrue(os.path.exists(repo.checkout_path_repo_1))

        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            self.assertEqual(
                "the/package/asset_ok-branch-base.ma",
                checkout.checkout_asset_by_branch(
                    repo.test_local_path_2,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base"
                )
            )
        self.assertTrue(os.path.exists(repo.checkout_path_repo_2))

    def test_checkout_by_tag(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            tag.create_tag_light_from_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base", "first_tag"
            )
            checkout_path = "the/package/asset_ok-tag-first_tag.ma"
            self.assertEqual(
                checkout_path,
                checkout.checkout_asset_by_tag(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "first_tag"
                )
            )
            self.assertTrue(os.path.exists(
                os.path.join(repo.test_local_path_1, checkout_path))
            )

    def test_checkout_by_commit(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            fetch.fetch(repo.test_local_path_1, vit_connection)
            first_commit = commit.list_commits(
                repo.test_local_path_1,
                repo.package_ok,
                repo.asset_ok
            )[0]
        # with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
        # FIXME: connecing twice will cause crash !!!
            checkout_path = checkout.checkout_asset_by_commit(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                first_commit
            )
        self.assertTrue(os.path.exists(
            os.path.join(
                repo.test_local_path_1,
                checkout_path
            )
        ))

    def test_checkout_package_not_found(self):
        with self.assertRaises(Package_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                checkout.checkout_asset_by_branch(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ko,
                    repo.asset_ok,
                    "base"
                )

    def test_checkout_asset_not_found(self):
        with self.assertRaises(Asset_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                checkout.checkout_asset_by_branch(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ko,
                    "base"
                )

    def test_checkout_branch_not_found(self):
        with self.assertRaises(Branch_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                checkout.checkout_asset_by_branch(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "non_existing_branch"
                )

    def test_checkout_as_editable(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                editable=True
            )

    def test_checkout_as_editable_but_already_has_editor(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                editable=True
            )
        with self.assertRaises(Asset_AlreadyEdited_E):
            with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
                # fetch.fetch(repo.test_local_path_2, vit_connection)
                checkout.checkout_asset_by_branch(
                    repo.test_local_path_2,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base",
                    editable=True
                )

    def test_double_checkout_rebase(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
            )
        sha = py_helpers.calculate_file_sha(repo.checkout_path_repo_1)
        self._append_line_to_file(repo.checkout_path_repo_1, "bla bla")
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                rebase=True
            )
        self.assertEqual(
            sha,
            py_helpers.calculate_file_sha(repo.checkout_path_repo_1)
        )

    def test_double_checkout_no_rebase(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
            )
        self._append_line_to_file(repo.checkout_path_repo_1, "bla bla")
        sha = py_helpers.calculate_file_sha(repo.checkout_path_repo_1)
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
            )
        self.assertEqual(
            sha,
            py_helpers.calculate_file_sha(repo.checkout_path_repo_1)
        )

    def test_checkout_file_by_branch_but_file_was_deleted(self):
        self._rm_dir(
            os.path.join(
                repo.test_origin_path_ok,
                repo.package_ok
            )
        )
        with self.assertRaises(Path_FileNotFoundAtOrigin_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                checkout.checkout_asset_by_branch(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base",
                )
            checkout.checkout_asset_by_branch(
                self.test_local_path_1,
                self.package_ok,
                self.asset_ok,
                "base"
            )

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
