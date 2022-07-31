import os
import shutil
import unittest
import glob

from context import vit
from vit import main_commands
from vit import command_line_lib

import logging
log = logging.getLogger()
logging.basicConfig()

class TestInitOriginRepo(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_origin_path_ko = "nupes/origin_repo"
    test_local_path_ok = "tests/local_repo"
    test_local_path_ko = "nupes/local_repo"

    def setUp(self):
        self._clean_dir()

    def atearDown(self):
        self._clean_dir()

    def test_create_asset_from_local_modify_and_push(self): 
        main_commands.init_origin(self.test_origin_path_ok)

        main_commands.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

        main_commands.create_package(self.test_local_path_ok, "assets/elephant", True)

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

        main_commands.commit(self.test_local_path_ok)

        file = glob.glob("tests/local_repo/assets/elephant/elephant_mod/elephant_mod*")[0]
        self._append_line_to_file(file, "some modification")

        main_commands.commit(self.test_local_path_ok)

        main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        main_commands.branch_from_origin_branch(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            "low_poly"
        )

        main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "low_poly",
            editable=True
        )

        main_commands.fetch_asset(
            self.test_local_path_ok,
            "assets/elephant",
            "elephant_mod",
            "base",
            editable=True
        )

        command_line_lib.log_current_status(self.test_local_path_ok)

    def _clean_dir(self):
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_ok):
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
