import os
import unittest

from vit.custom_exceptions import *
from vit.vit_lib import (
    checkout, commit,
    rebase
)

from tests import vit_test_repo as repo
from vit.connection.vit_connection import ssh_connect_auto


class TestRebase(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_rebase_from_commit(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit_file = commit.commit_file(
                repo.test_local_path_1,
                vit_connection,
                checkout_file,
                "commit 1",
                keep_editable=True,
                keep_file=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit.commit_file(
                repo.test_local_path_1,
                vit_connection,
                checkout_file,
                "commit 2"
            )
            rebase.rebase_from_commit(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base", commit_file
            )

    def test_rebase_from_commit_on_unknown_branch(self):
        with self.assertRaises(Branch_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                rebase.rebase_from_commit(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "branch does not exist", "nupe"
                )

    def test_rebase_from_commit_on_unknown_commit(self):
        with self.assertRaises(Commit_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                rebase.rebase_from_commit(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base", "nupe"
                )

    def test_rebase_from_commit_but_already_edited(self):
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                repo.test_local_path_2,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_2, "ouiii")
            commit_file = commit.commit_file(
                repo.test_local_path_2,
                vit_connection,
                checkout_file,
                "commit 1",
                keep_editable=True,
                keep_file=True
            )
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            with self.assertRaises(Asset_AlreadyEdited_E):
                rebase.rebase_from_commit(
                    repo.test_local_path_1,
                    vit_connection, repo.package_ok,
                    repo.asset_ok, "base", commit_file
                )

    def test_rebase_from_commit_but_file_deleted_on_origin(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            commit_file = commit.commit_file(
                repo.test_local_path_1,
                vit_connection,
                checkout_file,
                "commit 1",
                keep_editable=True,
                keep_file=True
            )
            os.remove(os.path.join(repo.test_origin_path_ok, commit_file))
            with self.assertRaises(Path_FileNotFoundAtOrigin_E):
                rebase.rebase_from_commit(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base", commit_file
                )

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
