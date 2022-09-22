import shutil
import unittest

from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.vit_lib import (
    repo_init_clone,
    package, asset,
    asset_template,
    checkout, commit,
    update, tag
)

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

class TestUpdate(unittest.TestCase):

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

    def test_update_when_late_from_one_commit(self):
        checkout_file_repo_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1, self.package_ok,
            self.asset_ok, "base", editable=True
        )
        checkout_file_repo_2 = checkout.checkout_asset_by_branch(
            self.test_local_path_2, self.package_ok,
            self.asset_ok, "base"
        )
        self._append_line_to_file(self.checkout_path_repo_1, "ouiii")
        commit.commit_file(
            self.test_local_path_1, checkout_file_repo_1, "new commit",
            keep_file=True, keep_editable=True
        )
        update.update(self.test_local_path_2, checkout_file_repo_2)

    def test_update_exchange_file_between_two_repo(self):
        # checkout on repo 1 and commit 1.
        checkout_file_repo_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1, self.package_ok,
            self.asset_ok, "base", editable=True
        )
        checkout_file_repo_2 = checkout.checkout_asset_by_branch(
            self.test_local_path_2, self.package_ok,
            self.asset_ok, "base"
        )
        self._append_line_to_file(self.checkout_path_repo_1, "1")
        commit.commit_file(
            self.test_local_path_1, checkout_file_repo_1, "1",
            keep_file=True,
        )
        # update on repo 2 and commit 2.
        update.update(self.test_local_path_2, checkout_file_repo_2, editable=True)
        self._append_line_to_file(self.checkout_path_repo_2, "2")
        commit.commit_file(
            self.test_local_path_2,
            checkout_file_repo_2, "2",
            keep_file=True
        )
        # update on repo 1 and commit 3
        update.update(self.test_local_path_1, checkout_file_repo_1, editable=True)
        self._append_line_to_file(self.checkout_path_repo_1, "3")
        commit.commit_file(
            self.test_local_path_1,
            checkout_file_repo_1, "3",
            keep_file=True
        )
        # update on repo 2.
        update.update(self.test_local_path_2, checkout_file_repo_2)

    def test_update_on_tag(self):
        tag_id = "NEW_TAG"
        tag.create_tag_light_from_branch(
            self.test_local_path_1, self.package_ok,
            self.asset_ok, "base", tag_id
        )
        tag_checkout = checkout.checkout_asset_by_tag(
            self.test_local_path_1, self.package_ok,
            self.asset_ok, tag_id
        )
        with self.assertRaises(Asset_UpdateOnNonBranchCheckout_E):
            update.update(self.test_local_path_1, tag_checkout)

    def test_reset_local_change(self):
        checkout_file_repo_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1, self.package_ok,
            self.asset_ok, "base", editable=True
        )
        checkout_file_repo_2 = checkout.checkout_asset_by_branch(
            self.test_local_path_2, self.package_ok,
            self.asset_ok, "base"
        )
        self._append_line_to_file(self.checkout_path_repo_1, "1")
        commit.commit_file(
            self.test_local_path_1, checkout_file_repo_1, "1",
            keep_file=True,
        )
        self._append_line_to_file(self.checkout_path_repo_2, "2")
        with self.assertRaises(Asset_ChangeNotCommitted_E):
            update.update(self.test_local_path_2, checkout_file_repo_2)
        update.update(self.test_local_path_2, checkout_file_repo_2, rebase=True)

    def test_update_already_up_to_date(self):
        checkout_file_repo_1 = checkout.checkout_asset_by_branch(
            self.test_local_path_1,
            self.package_ok,
            self.asset_ok, "base"
        )
        with self.assertRaises(Asset_AlreadyUpToDate_E):
            update.update(self.test_local_path_1, checkout_file_repo_1)
        update.update(self.test_local_path_1, checkout_file_repo_1, editable=True)
        self._append_line_to_file(self.checkout_path_repo_1, "1")
        commit.commit_file(self.test_local_path_1, checkout_file_repo_1, "1")

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