import os
import shutil
import unittest
import glob

from context import vit
from vit.vit_connection import VitConnection
from vit import main_commands
from vit import command_line_lib

from vit.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

import logging
log = logging.getLogger()
logging.basicConfig()

class TestInitOriginRepo(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_origin_path_ko = "nupes/origin_repo"
    test_local_path_ok = "tests/local_repo"
    test_local_path_ko = "nupes/local_repo"
    test_local_path_2  = "tests/local_repo2"

    def setUp(self):
        VitConnection.SSHConnection = FakeSSHConnection
        self._clean_dir()

    def atearDown(self):
        VitConnection.SSHConnection = SSHConnection
        self._clean_dir()

    def atest_create_asset_fetch_and_commit(self):
        self.assertTrue(main_commands.init_origin(self.test_origin_path_ok))
        self.assertTrue(main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        ))
        self.assertTrue(main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        ))
        self.assertTrue(main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
        ))
        self.assertTrue(main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        ))
        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        ))

        file = glob.glob(
            "tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        command_line_lib.log_current_status(self.test_local_path_ok)
        self.assertTrue(main_commands.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma"
        ))

    def atest_create_asset_fetch_and_commit_but_keep_it(self):
        self.assertTrue(main_commands.init_origin(self.test_origin_path_ok))
        self.assertTrue(main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        ))
        self.assertTrue(main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        ))
        self.assertTrue(main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
        ))
        self.assertTrue(main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        ))
        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        ))

        file = glob.glob(
            "tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        command_line_lib.log_current_status(self.test_local_path_ok)
        self.assertTrue(main_commands.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            keep=True
        ))

    def atest_create_asset_and_fetch_it_as_readonly(self):

        main_commands.init_origin(self.test_origin_path_ok)

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        )

        main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
       )

        main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        )

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        ))

        self.assertFalse(main_commands.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma"
        ))

    def atest_fetch_asset_as_readonly_modify_it_then_fetch_it_as_editable(self):

        main_commands.init_origin(self.test_origin_path_ok)

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        )

        main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
       )

        main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        )

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        ))

        file = glob.glob("tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        ))

        self.assertTrue(main_commands.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma"
        ))

    def atest_fetch_asset_as_readonly_modify_it_then_fetch_it_as_editable_but_rebase(self):

        main_commands.init_origin(self.test_origin_path_ok)

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        )

        main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
       )

        main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        )

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        ))

        file = glob.glob("tests/local_repo/assets/elephant/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True,
            rebase=True
        ))

        self.assertFalse(main_commands.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma"
        ))

    def atest_fetch_asset_as_editable_but_already_as_editor(self):


        main_commands.init_origin(self.test_origin_path_ok)

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_2,
            "yuhuali", "localhost"
        )

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        )

        main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
       )

        main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        )

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        ))

        self.assertFalse(main_commands.fetch_asset(
            self.test_local_path_2,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        ))

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_2,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=False
        ))

    def test_create_asset_branch_it_and_fetch_both(self):
        main_commands.init_origin(self.test_origin_path_ok)

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        )

        main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
        )

        main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        )

        self.assertTrue(main_commands.branch_from_origin_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            "low_poly"
        ))

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "low_poly",
            editable=True
        ))

        main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        command_line_lib.log_current_status(self.test_local_path_ok)

        self._append_line_to_file(
            "tests/local_repo/assets/elephant/elephant_mod-low_poly.ma",
            "some modification")

        self.assertTrue(
            main_commands.commit_file(
                self.test_local_path_ok,
                "assets/elephant/elephant_mod-low_poly.ma"
            ))

        self.assertTrue(main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
           "elephant_mod",
            "low_poly",
            editable=False
        ))

        command_line_lib.log_current_status(self.test_local_path_ok)

    def test_tag_from_branch(self):
        main_commands.init_origin(self.test_origin_path_ok)

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

        main_commands.create_package(
            self.test_local_path_ok,
            "assets/elephant", True
        )

        main_commands.create_template_asset_maya(
            self.test_local_path_ok, "mod",
            "tests/init_repo/mod_template.ma"
        )

        main_commands.create_asset_maya(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "mod"
        )

        main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        self._append_line_to_file(
            "tests/local_repo/assets/elephant/elephant_mod-base.ma",
            "some modification")

        main_commands.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            keep=True
        )

        self.assertTrue(main_commands.create_tag_light_from_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base", "myFirstTag"
        ))

        self._append_line_to_file(
            "tests/local_repo/assets/elephant/elephant_mod-base.ma",
            "some modification")

        main_commands.commit_file(
            self.test_local_path_ok,
            "assets/elephant/elephant_mod-base.ma",
            keep=True
        )

    def _clean_dir(self):
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_ok,
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
