import shutil
import unittest
from vit.command_line_lib import log
from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.vit_lib import (
    repo_init_clone,
    package, asset,
    asset_template,
    checkout, tag,
    commit, branch
)

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

class TestLog(unittest.TestCase):

    print_log = False

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

    def test_graph_heavy(self):

        # checkout and commit "1" on base

        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "base", True
        )
        self._append_line_to_file(os.path.join(
            self.test_local_path_1, checkout_file), "1"
        )
        commit.commit_file(
            self.test_local_path_1, checkout_file, "1", True, True
        )

        # branching "branch_1" from base and commit 2 on branch 1

        branch.create_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_1", branch_parent="base", create_tag=True
        )
        checkout_file_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_1", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_1), "2")
        commit.commit_file(
            self.test_local_path_1, checkout_file_1, "2", True, True
        )

        # commit 3 on branch 1

        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "3")
        commit.commit_file(
            self.test_local_path_1, checkout_file, "3", True, True
        )
        tag.create_tag_light_from_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_1", "my_first_tag"
        )

        # commit 4 on branch 1

        self._append_line_to_file(os.path.join(
            self.test_local_path_1, checkout_file_1), "4"
        )
        commit.commit_file(
            self.test_local_path_1, checkout_file_1, "4", True, True
        )
        tag.create_tag_annotated_from_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_1", "tag_annotated_test", "blou blou blou"
        )
        tag.create_tag_light_from_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_1", "oups_i_tagged_again"
        )

        # branch_2 from base.
        branch.create_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_2", branch_parent="base", create_tag=True
        )

        # branch_2 from base.
        branch.create_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_2_1", branch_parent="branch_2", create_tag=True
        )

        # branch_2 from base.
        branch.create_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_2_2", branch_parent="branch_2", create_tag=True
        )

        # commit 5 on branch_1
        self._append_line_to_file(os.path.join(
            self.test_local_path_1, checkout_file), "5"
        )
        commit.commit_file(
            self.test_local_path_1, checkout_file, "5", True, True
        )

        # commit 6 on branch_1
        self._append_line_to_file(os.path.join(
            self.test_local_path_1, checkout_file_1), "6"
        )
        commit.commit_file(
            self.test_local_path_1, checkout_file_1, "6", True, True
        )

        # branch_3 from base and checkout.
        branch.create_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_3", branch_parent="base", create_tag=True
        )
        checkout_file_2 = checkout.checkout_asset_by_branch(
            self.test_local_path_1, self.package_ok, self.asset_ok,
            "branch_2", True
        )

        # commit 7 on branch_3
        self._append_line_to_file(os.path.join(
            self.test_local_path_1, checkout_file_2), "7"
        )
        commit.commit_file(
            self.test_local_path_1, checkout_file_2, "7", True, True
        )

        # commit 8 on branch_1
        self._append_line_to_file(os.path.join(
            self.test_local_path_1, checkout_file), "8"
        )
        commit.commit_file(
            self.test_local_path_1, checkout_file, "8", True, True
        )
        a = log.get_log_lines(self.test_local_path_1, self.package_ok, self.asset_ok)
        if self.print_log:
            for l in a: print(l)

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
