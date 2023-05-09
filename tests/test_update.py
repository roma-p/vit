import unittest

from vit.custom_exceptions import *
from vit.vit_lib import (checkout, commit, update, tag)

from tests import vit_test_repo as repo
from vit.connection.connection_utils import ssh_connect_auto


class TestUpdate(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_update_when_late_from_one_commit(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file_repo_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", editable=True
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            checkout_file_repo_2 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok, "base"
            )
        self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "new commit",
                keep_file=True, keep_editable=True
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            update.update(
                vit_connection,
                checkout_file_repo_2
            )

    def test_update_exchange_file_between_two_repo(self):
        # checkout on repo 1 and commit 1.
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file_repo_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok, "base", editable=True
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            checkout_file_repo_2 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok, "base"
            )
        self._append_line_to_file(repo.checkout_path_repo_1, "1")
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "1",
                keep_file=True,
            )
        # update on repo 2 and commit 2.
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            update.update(
                vit_connection,
                checkout_file_repo_2, editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_2, "2")
            commit.commit_file(
                vit_connection,
                checkout_file_repo_2, "2",
                keep_file=True
            )
        # update on repo 1 and commit 3
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            update.update(
                vit_connection,
                checkout_file_repo_1, editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "3")
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "3",
                keep_file=True
            )
        # update on repo 2.
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            update.update(
                vit_connection,
                checkout_file_repo_2
            )

    def test_update_on_tag(self):
        tag_id = "NEW_TAG"

        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            tag.create_tag_light_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", tag_id
            )
            tag_checkout = checkout.checkout_asset_by_tag(
                vit_connection,
                repo.package_ok, repo.asset_ok, tag_id
            )
            with self.assertRaises(Asset_UpdateOnNonBranchCheckout_E):
                update.update(
                    vit_connection,
                    tag_checkout
                )

    def test_reset_local_change(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file_repo_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", editable=True
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            checkout_file_repo_2 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok, "base"
            )
        self._append_line_to_file(repo.checkout_path_repo_1, "1")
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "1", keep_file=True,
            )
        self._append_line_to_file(repo.checkout_path_repo_2, "2")
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            with self.assertRaises(Asset_ChangeNotCommitted_E):
                update.update(
                    vit_connection,
                    checkout_file_repo_2
                )
            update.update(
                vit_connection,
                checkout_file_repo_2,
                reset=True
            )

    def test_update_already_up_to_date(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file_repo_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok, "base"
            )
            with self.assertRaises(Asset_AlreadyUpToDate_E):
                update.update(
                    vit_connection,
                    checkout_file_repo_1
                )
            update.update(
                vit_connection,
                checkout_file_repo_1,
                editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "1")
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "1"
            )

    def test_fetch_up_to_date_asset_and_update_it_as_editable(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file_repo_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "1")
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "1", keep_file=True,
            )
            update.update(
                vit_connection,
                checkout_file_repo_1, editable=True
            )

    def test_update_as_editable_and_reset(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file_repo_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", editable=True
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "1")
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "1",
                keep_file=True,
            )
            self._append_line_to_file(repo.checkout_path_repo_1, "2")
            update.update(
                vit_connection,
                checkout_file_repo_1,
                editable=True, reset=True
            )

    def test_update_as_editable_but_no_reset_despite_not_beeing_late_on_branch(self):
        # checkout on repo 1 and commit 1.
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            checkout_file_repo_1 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", editable=True
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            checkout_file_repo_2 = checkout.checkout_asset_by_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok, "base"
            )
        self._append_line_to_file(repo.checkout_path_repo_1, "1")
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            commit.commit_file(
                vit_connection,
                checkout_file_repo_1, "1",
                keep_file=True,
            )
        # update on repo 2 and commit 2.
        self._append_line_to_file(repo.checkout_path_repo_2, "2")
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            with self.assertRaises(Asset_ChangeNotCommitted_E):
                update.update(
                    vit_connection,
                    checkout_file_repo_2, editable=True
                )

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
