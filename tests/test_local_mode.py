import os
import unittest

import context

from vit.connection.connection_utils import ssh_connect_auto
from vit.custom_exceptions import *
from vit.connection.vit_connection import VitConnection
from vit.connection.vit_connection_local import VitConnectionLocal
from tests.fake_ssh_connection import FakeSSHConnection
from tests import vit_test_repo as repo

from vit.vit_lib import (
    repo_init_clone,
    package, asset,
    asset_template,
    checkout, update,
    commit
)


class TestLocalMode(unittest.TestCase):

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)

    def setUp(self):
        VitConnection.SSHConnection = FakeSSHConnection
        repo._clean_dir()
        repo_init_clone.init_origin(repo.test_origin_path_ok)

        origin_path_abs = os.path.abspath(repo.test_origin_path_ok)
        vit_connection = VitConnectionLocal(
            repo.test_local_path_1, "prout",
            origin_path_abs, "user1"
        )
        with vit_connection:
            repo_init_clone.clone(
                vit_connection,
                origin_path_abs,
                repo.test_local_path_1,
                "user1", False
            )

            asset_template.create_asset_template(
                vit_connection,
                repo.template_id,
                repo.template_file_path
            )

            package.create_package(
                vit_connection,
                repo.package_ok,
                force_subtree=True
            )

            asset.create_asset_from_template(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                repo.template_id
            )

    def test_local_repo(self):

        origin_path_abs = os.path.abspath(repo.test_origin_path_ok)
        vit_connection = VitConnectionLocal(
            repo.test_local_path_1, "prout",
            origin_path_abs, "user1"
        )
        with vit_connection:
            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base"
            )
            self.assertEqual(
                "the/package/asset_ok-branch-base.ma",
                checkout_file
            )
            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self.assertTrue(os.path.islink(repo.checkout_path_repo_1))

            checkout_file = checkout.checkout_asset_by_branch(
                vit_connection,
                os.path.join(repo.package_ok, repo.asset_ok),
                "base",
                editable=True
            )

            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self.assertFalse(os.path.islink(repo.checkout_path_repo_1))

            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")

            commit.commit_file(
                vit_connection,
                checkout_file,
                "new commit",
                keep_file=True,
                keep_editable=True
            )

            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self.assertFalse(os.path.islink(repo.checkout_path_repo_1))

            self._append_line_to_file(repo.checkout_path_repo_1, "ouiii")

            commit.commit_file(
                vit_connection,
                checkout_file,
                "new commit",
                keep_file=True,
                keep_editable=False
            )

            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self.assertTrue(os.path.islink(repo.checkout_path_repo_1))

            update.update(vit_connection, checkout_file, editable=True)

            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self.assertFalse(os.path.islink(repo.checkout_path_repo_1))

            commit.release_editable(
                vit_connection,
                checkout_file
            )

            self.assertTrue(os.path.exists(repo.checkout_path_repo_1))
            self.assertTrue(os.path.islink(repo.checkout_path_repo_1))


if __name__ == "__main__":
    unittest.main()
