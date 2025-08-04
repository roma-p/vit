import os
import unittest

from vit.connection.connection_utils import ssh_connect_auto
from vit.custom_exceptions import *
from vit.vit_lib import (branch, tag, fetch)

from tests import vit_test_repo as repo


class TestBranch(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_create_branch(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            branch.create_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "new_branch",
                branch_parent="base",
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            fetch.fetch(vit_connection)
        self.assertSetEqual(
            {"base", "new_branch"},
            set(branch.list_branches(
                repo.test_local_path_2,
                os.path.join(repo.package_ok, repo.asset_ok),
            ))
        )

    def test_create_branch_from_another_branch_but_origin_branch_not_found(self):
        with self.assertRaises(Branch_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                branch.create_branch(
                    vit_connection,
                    os.path.join(repo.package_ok, repo.asset_ok),
                    "new_branch",
                    branch_parent="branch_not_found",
                )

    def _test_create_branch_from_another_branch_but_new_branch_already_exists(self):
        with self.assertRaises(Branch_AlreadyExist_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                branch.create_branch(
                    vit_connection,
                    os.path.join(repo.package_ok, repo.asset_ok),
                    "base",
                    branch_parent="base"
                )

    def test_create_branch_from_another_branch_and_create_tag(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            branch.create_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "new_base",
                branch_parent="base",
                create_tag=True
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            fetch.fetch(vit_connection)
        self.assertTupleEqual(
            ('asset_ok-new_base-v0.1.0',),
            tag.list_tags(
                repo.test_local_path_1,
                os.path.join(repo.package_ok, repo.asset_ok),
            )
        )

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
