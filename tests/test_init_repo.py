import shutil
import unittest
import glob

from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.commands import repo_init_clone

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

import logging
log = logging.getLogger()
logging.basicConfig()

class TestInitRepo(unittest.TestCase):

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

    def tearDown(self):
        VitConnection.SSHConnection = SSHConnection
        self._clean_dir()

    def _clean_dir(self):
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_ok,
                self.test_local_path_2):
            self._rm_dir(path)

    def test_init_and_clone_repo(self):
        repo_init_clone.init_origin(self.test_origin_path_ok)
        repo_init_clone.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )

    def test_init_when_dir_already_exists(self):
        repo_init_clone.init_origin(self.test_origin_path_ok)
        with self.assertRaises(Path_AlreadyExists_E):
            repo_init_clone.init_origin(self.test_origin_path_ok)

    def test_init_invalid_path(self):
        with self.assertRaises(Path_ParentDirNotExist_E):
            repo_init_clone.init_origin(self.test_origin_path_ko)

    def test_clone_when_dir_already_exists(self):
        repo_init_clone.init_origin(self.test_origin_path_ok)
        repo_init_clone.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        )
        with self.assertRaises(Path_AlreadyExists_E):
            repo_init_clone.clone(
                os.path.abspath(self.test_origin_path_ok),
                self.test_local_path_ok,
                "romainpelle", "localhost"
            )

    def test_clone_when_origin_not_exists(self):
        with self.assertRaises(OriginNotFound_E):
            repo_init_clone.clone(
                os.path.abspath(self.test_origin_path_ok),
                self.test_local_path_ok,
                "romainpelle", "localhost"
            )

    def test_clone_when_origin_is_not_a_repository(self):
        os.makedirs(self.test_origin_path_ok)
        with self.assertRaises(OriginNotFound_E):
            repo_init_clone.clone(
                os.path.abspath(self.test_origin_path_ok),
                self.test_local_path_ok,
                "romainpelle", "localhost"
            )

    def test_clone_when_origin_is_not_a_repository(self):
        with self.assertRaises(Path_ParentDirNotExist_E):
            repo_init_clone.clone(
                os.path.abspath(self.test_origin_path_ok),
                self.test_local_path_ko,
                "romainpelle", "localhost"
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
