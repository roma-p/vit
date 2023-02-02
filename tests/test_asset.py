import shutil
import unittest

from vit.connection.vit_connection import ssh_connect_auto
from vit.connection.vit_connection import VitConnection
from vit.custom_exceptions import *
from vit.vit_lib import (
    repo_init_clone,
    package, asset,
    asset_template,
    fetch
)

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

class TestAsset(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_local_path_1 = "tests/local_repo1"
    test_local_path_2 = "tests/local_repo2"
    package_ok = "the/package"
    package_ko = "the/package/nupe"
    template_file_path = "tests/test_data/mod_template.ma"
    template_id = "mod"

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

    def test_create_asset(self):
        asset.create_asset_from_template(
            self.test_local_path_1,
            self.package_ok,
            "asset_1",
            self.template_id
        )
        asset.create_asset_from_template(
            self.test_local_path_1,
            self.package_ok,
            "asset_2",
            self.template_id
        )

        with ssh_connect_auto(self.test_local_path_1) as ssh_connection:
            fetch.fetch(self.test_local_path_1, ssh_connection)
        with ssh_connect_auto(self.test_local_path_2) as ssh_connection:
            fetch.fetch(self.test_local_path_2, ssh_connection)

        self.assertSetEqual(
            {"asset_1", "asset_2"},
            set(asset.list_assets(
                self.test_local_path_1,
                self.package_ok
            ))
        )
        self.assertSetEqual(
            {"asset_1", "asset_2"},
            set(asset.list_assets(
                self.test_local_path_2,
                self.package_ok
            ))
        )

    def test_create_asset_but_template_not_found(self):
        with self.assertRaises(Template_NotFound_E):
            asset.create_asset_from_template(
                self.test_local_path_1,
                self.package_ok,
                "asset_1",
                "non_existing_template"
            )

    def test_create_asset_but_package_not_found(self):
        with self.assertRaises(Package_NotFound_E):
            asset.create_asset_from_template(
                self.test_local_path_1,
                self.package_ko,
                "asset_1",
                self.template_id
            )

    def test_create_asset_but_asset_already_exists(self):
        asset.create_asset_from_template(
            self.test_local_path_1,
            self.package_ok,
            "asset_1",
            self.template_id
            )
        with self.assertRaises(Asset_AlreadyExists_E):
            asset.create_asset_from_template(
                self.test_local_path_2,
                self.package_ok,
                "asset_1",
                self.template_id
            )

    def test_create_asset_from_file(self):
        asset.create_asset_from_file(
            self.test_local_path_1,
            self.package_ok,
            "asset_1",
            self.template_file_path
        )
        self.assertSetEqual(
            {"asset_1"},
            set(asset.list_assets(
                self.test_local_path_1,
                self.package_ok
            ))
        )

    def test_create_asset_from_file_but_file_not_found(self):
        with self.assertRaises(Path_FileNotFound_E):
            asset.create_asset_from_file(
                self.test_local_path_1,
                self.package_ok,
                "asset_1",
               "file_not_found.ma"
            )

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

if __name__ == '__main__':
    unittest.main()
