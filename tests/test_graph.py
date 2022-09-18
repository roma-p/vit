import shutil
import unittest
import time
from vit import py_helpers, graph
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

class TestGraph(unittest.TestCase):

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

    def atearDown(self):
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

    def atest_graph_single_commit(self):
        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "1")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "1", True, True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "2")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "2", True, True
        )
        a = graph.gen_graph_data(self.test_local_path_1, self.package_ok, self.asset_ok)
        for l in a: print(l)

    def atest_graph_no_commit_after_branch(self):
        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "1")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "1", True, True
        )
        time.sleep(1)
        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", "branch_1"
        )
        #branch.branch_from_origin_branch(
        #    self.test_local_path_1,
        #    self.package_ok,
        #    self.asset_ok,
        #    "base", "branch_2"
        #)
        checkout_file_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "branch_1", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_1), "2")
        time.sleep(1)
        commit.commit_file(
            self.test_local_path_1,
            checkout_file_1,
            "2", True, True
        )
        time.sleep(1)
        a = graph.gen_graph_data(self.test_local_path_1, self.package_ok, self.asset_ok)
        for l in a: print(l)

    def atest_graph_three_br_no_commit_after_branch(self):
        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "1")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "1", True, True
        )
        time.sleep(1)
        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", "branch_1"
        )
        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", "branch_2"
        )
        a = graph.gen_graph_data(self.test_local_path_1, self.package_ok, self.asset_ok)
        for l in a: print(l)

    def atest_graph_two_branches(self):
        # one commit on trunk / on commit on each branch.
        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "1")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "1", True, True
        )
        time.sleep(1)
        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", "branch_1"
        )
        checkout_file_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "branch_1", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_1), "2")
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "3")
        time.sleep(1)
        commit.commit_file(
            self.test_local_path_1,
            checkout_file_1,
            "2", True, True
        )
        time.sleep(1)
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "3", True, True
        )
        a = graph.gen_graph_data(self.test_local_path_1, self.package_ok, self.asset_ok)
        for l in a: print(l)

    def test_graph_four_branches_from_same_commit(self):
        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "1")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "1", True, True
        )
        time.sleep(1)
        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", "branch_1"
        )
        #branch.branch_from_origin_branch(
        #    self.test_local_path_1,
        #    self.package_ok,
        #    self.asset_ok,
        #    "base", "branch_2"
        #)
        #branch.branch_from_origin_branch(
        #    self.test_local_path_1,
        #    self.package_ok,
        #    self.asset_ok,
        #    "base", "branch_3"
        #)

        checkout_file_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "branch_1", True
        ) 
        #checkout_file_2 = checkout.checkout_asset_by_branch(
        #    self.test_local_path_1,
        #    self.package_ok,
        #    self.asset_ok,
        #    "branch_2", True
        #) 
        #checkout_file_3 = checkout.checkout_asset_by_branch(
        #    self.test_local_path_1,
        #    self.package_ok,
        #    self.asset_ok,
        #    "branch_3", True
        #)

        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "2")
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_1), "3")
        #self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_2), "4")
        #self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_3), "5")

        commit.commit_file(self.test_local_path_1, checkout_file, "2", True, True)
        commit.commit_file(self.test_local_path_1, checkout_file_1, "3", True, True)
        #commit.commit_file(self.test_local_path_1, checkout_file_2, "4", True, True)
        #commit.commit_file(self.test_local_path_1, checkout_file_3, "5", True, True)

        a = graph.gen_graph_data(self.test_local_path_1, self.package_ok, self.asset_ok)
        for l in a : print(l)

    def atest_graph_three_branches(self):

        # checkout and commit "1" on base

        checkout_file = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "1")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "1", True, True
        )
        time.sleep(1)

        # branching "branch_1" from base and commit "2" on branch 1

        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", "branch_1"
        )
        checkout_file_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "branch_1", True
        )
        time.sleep(1)
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_1), "2")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file_1,
            "2", True, True
        )

        # commit "3" on branch 2

        time.sleep(1)
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "3")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "3", True, True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_1), "4")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file_1,
            "4", True, True
        )
        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base", "branch_2"
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "5")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "5", True, True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_1), "6")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file_1,
            "6", True, True
        )
        branch.branch_from_origin_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "base",
            "branch_3"
        )
        checkout_file_2 = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok,
            "branch_2", True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file_2), "7")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file_2,
            "7", True, True
        )
        self._append_line_to_file(os.path.join(self.test_local_path_1, checkout_file), "8")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file,
            "8", True, True
        )
        a = graph.gen_graph_data(self.test_local_path_1, self.package_ok, self.asset_ok)


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
