import shutil
import unittest
import glob

from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.commands import repo_init_clone
from vit.commands import package

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

class TestPackage(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_local_path_1 = "tests/local_repo1"
    test_local_path_2 = "tests/local_repo2"
    test_package = "the/package"

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
            "romainpelle", "localhost"
        )
        repo_init_clone.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_2,
            "romainpelle", "localhost"
        )

    def _clean_dir(self):
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_1,
                self.test_local_path_2):
            self._rm_dir(path)

    def test_create_package(self):
        package.create_package(self.test_local_path_1, "path1")

    def test_create_package_but_already_exists(self):
        package.create_package(self.test_local_path_1, "path1")
        with self.assertRaises(Package_AlreadyExists_E):
            package.create_package(self.test_local_path_1, "path1")
        with self.assertRaises(Package_AlreadyExists_E):
            package.create_package(self.test_local_path_2, "path1")

    def test_create_package_but_parent_dir_does_not_exists(self):
        with self.assertRaises(Path_ParentDirNotExist_E):
            package.create_package(self.test_local_path_1, "/not/exists")

    def test_create_package_and_force_subtree(self):
        package.create_package(
            self.test_local_path_1,
            "new/package",
            force_subtree=True
        )

    def test_list_packages(self):
        package.create_package(self.test_local_path_1, "path1")
        package.create_package(self.test_local_path_1, "path2")
        self.assertSetEqual(
            {"path1", "path2"},
            set(package.list_packages(self.test_local_path_2))
        )

    @staticmethod
    def _rm_dir(directory):
        if os.path.exists(directory):
            shutil.rmtree(directory, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()

    @staticmethod
    def _rm_dir(directory):
        if os.path.exists(directory):
            shutil.rmtree(directory, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
