import os
import logging
import shutil
import unittest

from tests.fake_ssh_connection import FakeSSHConnection
from vit.connection.ssh_connection import SSHConnection
from vit.connection.vit_connection import VitConnection
from vit.connection.vit_connection_remote import VitConnectionRemote
from vit.custom_exceptions import *
from vit.vit_lib import repo_init_clone

log = logging.getLogger()
logging.basicConfig()


class TestInitRepo(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_origin_path_ko = "nupes/origin_repo"
    test_local_path_ok = "tests/local_repo"
    test_local_path_ko = "nupes/local_repo"
    test_local_path_2 = "tests/local_repo2"

    host = "localhost"
    user = "user"

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
        origin_path_abs = os.path.abspath(self.test_origin_path_ok)
        repo_init_clone.init_origin(origin_path_abs)
        vit_connection = VitConnectionRemote(
            self.test_local_path_ok, self.host,
            origin_path_abs, self.user
        )
        with vit_connection:
            repo_init_clone.clone(
                vit_connection,
                origin_path_abs,
                self.test_local_path_ok,
                self.user, True, self.host
            )

    def test_init_when_dir_already_exists(self):
        repo_init_clone.init_origin(self.test_origin_path_ok)
        with self.assertRaises(Path_AlreadyExists_E):
            repo_init_clone.init_origin(self.test_origin_path_ok)

    def test_init_invalid_path(self):
        with self.assertRaises(Path_ParentDirNotExist_E):
            repo_init_clone.init_origin(self.test_origin_path_ko)

    def test_clone_when_dir_already_exists(self):
        origin_path_abs = os.path.abspath(self.test_origin_path_ok)
        repo_init_clone.init_origin(self.test_origin_path_ok)
        vit_connection = VitConnectionRemote(
            self.test_local_path_ok, self.host,
            origin_path_abs, self.user
        )
        with vit_connection:
            repo_init_clone.clone(
                vit_connection,
                origin_path_abs,
                self.test_local_path_ok,
                self.user, True, self.host
            )
            with self.assertRaises(Path_AlreadyExists_E):
                repo_init_clone.clone(
                    vit_connection,
                    origin_path_abs,
                    self.test_local_path_ok,
                    self.user, True, self.host
                )

    def test_clone_when_origin_not_exists(self):
        origin_path_abs = os.path.abspath(self.test_origin_path_ok)
        vit_connection = VitConnectionRemote(
            self.test_local_path_ok, self.host,
            origin_path_abs, self.user
        )
        with self.assertRaises(OriginNotFound_E):
            with vit_connection:
                repo_init_clone.clone(
                    vit_connection,
                    origin_path_abs,
                    self.test_local_path_ok,
                    self.user, True, self.host
                )

    def test_clone_when_origin_is_not_a_repository(self):
        origin_path_abs = os.path.abspath(self.test_origin_path_ok)
        os.makedirs(self.test_origin_path_ok)
        vit_connection = VitConnectionRemote(
            self.test_local_path_ok, self.host,
            origin_path_abs, self.user
        )
        with self.assertRaises(OriginNotFound_E):
            with vit_connection:
                repo_init_clone.clone(
                    vit_connection,
                    origin_path_abs,
                    self.test_local_path_ok,
                    self.user, True, self.host
                )

    def test_clone_when_repo_is_not_a_repository(self):
        origin_path_abs = os.path.abspath(self.test_origin_path_ok)
        vit_connection = VitConnectionRemote(
            self.test_local_path_ko, self.host,
            origin_path_abs, self.user
        )
        with self.assertRaises(Path_ParentDirNotExist_E):
            with vit_connection:
                repo_init_clone.clone(
                    vit_connection,
                    origin_path_abs,
                    self.test_local_path_ko,
                    self.user, True, self.host
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
