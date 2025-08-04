import os
import shutil
import unittest

from vit.custom_exceptions import *
from vit.vit_lib import (
    checkout, commit
)

from tests import vit_test_repo as repo
from vit.connection.connection_utils import ssh_connect_auto


class TestCommit(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_commit(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit.commit_file(
                vit_connection,
                checkout_file,
                "new commit"
            )
            self.assertFalse(os.path.exists(repo.checkout_path_repo_1))

    def test_commit_non_existing_file(self):
        with self.assertRaises(Path_FileNotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                commit.commit_file(
                    vit_connection,
                    "non_existing_file",
                    "new commit"
                )

    def test_commit_untracked_file(self):
        shutil.copy(
            repo.template_file_path,
            os.path.join(
                repo.test_local_path_1,
                "untracked_file.ma"
            )
        )
        with self.assertRaises(Asset_UntrackedFile_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                commit.commit_file(
                    vit_connection,
                    "untracked_file.ma",
                    "new commit"
                )

    def test_commit_but_no_change(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=True
            )
            with self.assertRaises(Asset_NoChangeToCommit_E):
                commit.commit_file(
                    vit_connection,
                    checkout_file,
                    "new commit"
                )
        self.assertTrue(os.path.exists(repo.checkout_path_repo_1))

    def test_commit_but_file_not_editable(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=False
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            with self.assertRaises(Asset_NotEditable_E):
                commit.commit_file(
                    vit_connection,
                    checkout_file,
                    "new commit"
                )
        self.assertTrue(os.path.exists(repo.checkout_path_repo_1))

    def test_commit_and_keep_file(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit.commit_file(
                vit_connection,
                checkout_file,
                "new commit",
                keep_file=True
            )
            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            with self.assertRaises(Asset_NotEditable_E):
                commit.commit_file(
                    vit_connection,
                    checkout_file,
                    "new commit"
                )

    def test_commit_and_keep_file_and_editable(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit.commit_file(
                vit_connection,
                checkout_file,
                "new commit",
                keep_file=True,
                keep_editable=True
            )
            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit.commit_file(
                vit_connection,
                checkout_file,
                "new commit"
            )
            self.assertFalse(os.path.exists(repo.checkout_path_repo_1))

    def test_release_editable(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit.release_editable(
                vit_connection,
                checkout_file
            )
            with self.assertRaises(Asset_NotEditable_E):
                commit.commit_file(
                    vit_connection,
                    checkout_file,
                    "new commit"
                )

    def test_release_editable_but_file_is_not_editable(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=False
            )
            with self.assertRaises(Asset_NotEditable_E):
                commit.release_editable(
                    vit_connection,
                    checkout_file
                )

    def test_commit_twice(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit.commit_file(
                vit_connection,
                checkout_file,
                "new commit",
                keep_file=True,
                keep_editable=True
            )
            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            with self.assertRaises(Asset_NoChangeToCommit_E):
                commit.commit_file(
                    vit_connection,
                    checkout_file,
                    "new commit"
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
