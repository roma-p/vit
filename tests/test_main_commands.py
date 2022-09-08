import shutil
import unittest
import glob

from vit.connection.vit_connection import VitConnection
from vit import main_commands
from vit.custom_exceptions import *
from vit.commands import commit, checkout

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

import logging
log = logging.getLogger()
logging.basicConfig()

class TestInitOriginRepo(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_origin_path_ko = "nupes/origin_repo"
    test_local_path_ok = "tests/local_repo"
    test_local_path_ko = "nupes/local_repo"
    test_local_path_2 = "tests/local_repo2"

    elephant_mod_local_path = os.path.join(
        test_local_path_ok,
        "assets/elephant/elephant_mod-base.ma"
    )

    def setUp(self):
        VitConnection.SSHConnection = FakeSSHConnection
        self._clean_dir()
        self.init_default_repo()

    def tearDown(self):
        VitConnection.SSHConnection = SSHConnection
        self._clean_dir()

    def test_create_asset_from_template_checkout_and_commit(self):
        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )
        self.assertTrue(os.path.exists(self.elephant_mod_local_path))

        file = glob.glob("tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        commit.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            "commit_1"
        )
        self.assertFalse(os.path.exists(self.elephant_mod_local_path))

    def test_create_asset_checkout_and_commit_but_keep_it(self):
        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        file = glob.glob(
            "tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        commit.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            "commit_1",
            keep_file=True
        )
        self.assertTrue(os.path.exists(self.elephant_mod_local_path))

    def atest_create_asset_and_checkout_it_as_readonly(self):

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        )

        with self.assertRaises(Asset_NotEditable_E):
            commit.commit_file(
                self.test_local_path_ok,
                "assets/elephant/elephant_mod-base.ma",
                "commit_1"
            )

    def test_checkout_asset_as_readonly_modify_it_then_checkout_it_as_editable(self):

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        )

        file = glob.glob("tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        commit.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            "commit_1"
        )
        self.assertFalse(os.path.exists(self.elephant_mod_local_path))

    def test_checkout_asset_as_readonly_modify_it_then_checkout_it_as_editable_but_rebase(self):

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        )

        file = glob.glob("tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True,
            rebase=True
        )

        with self.assertRaises(Asset_NoChangeToCommit_E):
            commit.commit_file(
                self.test_local_path_ok,
                "assets/elephant/elephant_mod-base.ma",
                "commit_1"
            )

    def test_checkout_asset_as_editable_but_already_as_editor(self):

        # FIXME: IF not vit dir, not raise error.

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        with self.assertRaises(Asset_AlreadyEdited_E):
            checkout.checkout_asset_by_branch(
                self.test_local_path_2,
                "assets/elephant",
                "elephant_mod",
                "base",
                editable=True
            )

        checkout.checkout_asset_by_branch(
            self.test_local_path_2,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        )

    def test_create_asset_branch_it_and_checkout_both(self):

        main_commands.branch_from_origin_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            "low_poly"
        )

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "low_poly",
            editable=True
        )

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        self._append_line_to_file(
            "tests/local_repo/assets/elephant/elephant_mod-low_poly.ma",
            "some modification")

        commit.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-low_poly.ma",
            "commit_1"
        )

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "low_poly",
            editable=False
        )

    def test_list_packages(self):

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/lion",
        )

        self.assertEqual(
            {"assets/lion", "assets/elephant"},
            set(main_commands.list_packages(self.test_local_path_ok))
        )

    def atest_tag_from_branch(self):

        # FIXME: wrong exceptions.....
        # check tip of branch before editable....

        checkout.checkout_asset_by_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        self._append_line_to_file(
            "tests/local_repo/assets/elephant/elephant_mod-base.ma",
            "some modification")

        commit.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            "commit_1",
            keep_file=True,
            keep_editable=True,
        )

        main_commands.create_tag_light_from_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base", "myFirstTag"
        )

        self._append_line_to_file(
            "tests/local_repo/assets/elephant/elephant_mod-base.ma",
            "some modification")

        commit.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            "commit_1",
            keep_file=True,
            keep_editable=True,
        )

        checkout.checkout_asset_by_tag(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "myFirstTag",
        )

        with self.assertRaises(Asset_NotAtTipOfBranch):
            commit.commit_file(
                self.test_local_path_ok,
                "assets/elephant/elephant_mod-myFirstTag.ma",
                "commit_1"
            )

    def _clean_dir(self):
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_ok,
                self.test_local_path_2):
            self._rm_dir(path)

    def init_default_repo(self):
        main_commands.init_origin(self.test_origin_path_ok)
        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )
        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_2,
            "romainpelle", "localhost"
        )

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        )
        main_commands.create_template_asset(
            self.test_local_path_ok, "mod",
            "tests/test_data/mod_template.ma"
        )
        main_commands.create_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
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
