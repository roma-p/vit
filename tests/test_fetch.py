import shutil
import unittest

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


class TestFetch(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_local_path_1 = "tests/local_repo1"
    template_file_path = "tests/test_data/mod_template.ma"
    template_id = "mod"

    def setUp(self):
        VitConnection.SSHConnection = FakeSSHConnection
        self._clean_dir()
        self._init_repos()

    def tearDown(self):
        VitConnection.SSHConnection = SSHConnection
        self._clean_dir()


    def test_fetch(self):
        fetch.fetch(self.test_local_path_1)

    def test_get_repo_hierarchy(self):
        fetch.fetch(self.test_local_path_1)
        result = fetch.get_repo_hierarchy(self.test_local_path_1)
        expected =  {
            'package1': {
                'packages':{
                    'subpackage1':
                        {
                            'packages': {},
                            'assets': ("asset2", "asset3")
                        },
                    'subpackage2': {
                        'packages': {},
                        'assets': ()}
                },
                'assets': ("asset1",)
            },
            'package2': {
                'packages': {},
                'assets': ("asset4",)
            }
        }
        self.assertEqual(expected, result)

    def test_get_all_assets_info(self):
        fetch.fetch(self.test_local_path_1)
        result = fetch.get_all_assets_info(self.test_local_path_1)

    def _init_repos(self):
        repo_init_clone.init_origin(self.test_origin_path_ok)
        repo_init_clone.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_1,
            "romainpelle", "localhost"
        )
        asset_template.create_asset_template(
            self.test_local_path_1,
            self.template_id,
            self.template_file_path
        )
        package.create_package(
            self.test_local_path_1,
            "package1",
            force_subtree=True
        )
        package.create_package(
            self.test_local_path_1,
            "package2",
            force_subtree=True
        )
        package.create_package(
            self.test_local_path_1,
            "package1/subpackage1",
            force_subtree=True
        )
        package.create_package(
            self.test_local_path_1,
            "package1/subpackage2",
            force_subtree=True
        )
        asset.create_asset_from_template(
            self.test_local_path_1,
            "package1",
            "asset1",
            self.template_id
        )

        asset.create_asset_from_template(
            self.test_local_path_1,
            "package1/subpackage1",
            "asset2",
            self.template_id
        )

        asset.create_asset_from_template(
            self.test_local_path_1,
            "package1/subpackage1",
            "asset3",
            self.template_id
        )

        asset.create_asset_from_template(
            self.test_local_path_1,
            "package2",
            "asset4",
            self.template_id
        )

    def _clean_dir(self):
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_1):
            self._rm_dir(path)

    @staticmethod
    def _rm_dir(directory):
        if os.path.exists(directory):
            shutil.rmtree(directory, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
