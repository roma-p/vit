import unittest

from vit.custom_exceptions import *
from vit.vit_lib import (
    checkout, commit,
    clean
)

from tests import vit_test_repo as repo
from vit.connection.vit_connection import ssh_connect_auto


class TestClean(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_clean_editable_file_commited_and_released(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
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
            self.assertEqual(
                (checkout_file,),
                clean.get_files_to_clean(repo.test_local_path_1)["editable"])
            commit.release_editable(
                vit_connection,
                checkout_file)
            self.assertEqual(
                (checkout_file,),
                clean.get_files_to_clean(repo.test_local_path_1)["to_clean"])
            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
            self.assertEqual(
                (checkout_file,),
                clean.get_files_to_clean(repo.test_local_path_1)["changes"])

    def test_read_only_file_then_cleaned(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
            )
        self.assertEqual(
            (checkout_file,),
            clean.get_files_to_clean(repo.test_local_path_1)["to_clean"])
        clean.clean_files(repo.test_local_path_1, checkout_file)
        self.assertFalse(os.path.exists(
            os.path.join(
                repo.test_local_path_1,
                checkout_file
            )
        ))

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
