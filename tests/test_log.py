import os
import unittest
from vit.cli import vit_log_utils
from vit.vit_lib import (
    checkout, tag,
    commit, branch
)

from tests import vit_test_repo as repo
from vit.connection.connection_utils import ssh_connect_auto


class TestLog(unittest.TestCase):

    print_log = False

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_graph_heavy(self):

        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:

            # checkout and commit "1" on base

            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection, repo.package_ok, repo.asset_ok, "base", True
            )
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file), "1"
            )
            commit.commit_file(vit_connection, checkout_file, "1", True, True)

            # branching "branch_1" from base and commit 2 on branch 1

            branch.create_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_1", branch_parent="base", create_tag=True
            )
            checkout_file_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "branch_1", True
            )
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file_1), "2"
            )
            commit.commit_file(vit_connection, checkout_file_1, "2", True, True)

            # commit 3 on branch 1

            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file), "3"
            )
            commit.commit_file(vit_connection, checkout_file, "3", True, True)
            tag.create_tag_light_from_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_1", "my_first_tag"
            )

            # commit 4 on branch 1

            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file_1), "4"
            )
            commit.commit_file(vit_connection, checkout_file_1, "4", True, True)
            tag.create_tag_annotated_from_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_1", "tag_annotated_test", "blou blou blou"
            )
            tag.create_tag_light_from_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_1", "oups_i_tagged_again"
            )

            # branch_2 from base.
            branch.create_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_2", branch_parent="base", create_tag=True
            )

            # branch_2 from base.
            branch.create_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_2_1", branch_parent="branch_2", create_tag=True
            )

            # branch_2 from base.
            branch.create_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_2_2", branch_parent="branch_2", create_tag=True
            )

            # commit 5 on branch_1
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file), "5"
            )
            commit.commit_file(vit_connection, checkout_file, "5", True, True)

            # commit 6 on branch_1
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file_1), "6"
            )
            commit.commit_file(vit_connection, checkout_file_1, "6", True, True)

            # branch_3 from base and checkout.
            branch.create_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_3", branch_parent="base", create_tag=True
            )
            checkout_file_2 = checkout.checkout_asset_by_branch(
                vit_connection, repo.package_ok, repo.asset_ok,
                "branch_2", True
            )

            # commit 7 on branch_3
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file_2), "7"
            )
            commit.commit_file(vit_connection, checkout_file_2, "7", True, True)

            # commit 8 on branch_1
            self._append_line_to_file(os.path.join(
                repo.test_local_path_1, checkout_file), "8"
            )
            commit.commit_file(vit_connection, checkout_file, "8", True, True)
            a = vit_log_utils.get_log_lines(
                repo.test_local_path_1,
                repo.package_ok,
                repo.asset_ok
            )
            if self.print_log:
                for l in a: print(l)

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
