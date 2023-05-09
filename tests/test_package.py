import unittest

from vit.custom_exceptions import *
from vit.vit_lib import (
    package, fetch
)

from tests import vit_test_repo as repo
from vit.connection.connection_utils import ssh_connect_auto


class TestPackage(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_empty")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_create_package(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            package.create_package(
                vit_connection,
                "path1")

    def test_create_package_but_already_exists(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            package.create_package(
                vit_connection, "path1"
            )
            with self.assertRaises(Package_AlreadyExists_E):
                package.create_package(
                    vit_connection, "path1"
                )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            with self.assertRaises(Package_AlreadyExists_E):
                package.create_package(
                    vit_connection, "path1"
                )

    def test_create_package_but_parent_dir_does_not_exists(self):
        with self.assertRaises(Path_ParentDirNotExist_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                package.create_package(
                    vit_connection, "/not/exists"
                )

    def test_create_package_and_force_subtree(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            package.create_package(
                vit_connection,
                "new/package",
                force_subtree=True
            )

    def test_list_packages(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            package.create_package(vit_connection, "path1")
            package.create_package(vit_connection, "path2")

        with ssh_connect_auto(repo.test_local_path_2) as ssh_connection:
            fetch.fetch(ssh_connection)
        self.assertSetEqual(
            {"path1", "path2"},
            set(package.list_packages(repo.test_local_path_2))
        )


if __name__ == '__main__':
    unittest.main()
