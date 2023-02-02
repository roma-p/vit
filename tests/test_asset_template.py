import shutil
import unittest

from tests.fake_ssh_connection import FakeSSHConnection
from vit.connection.ssh_connection import SSHConnection
from vit.connection.vit_connection import VitConnection
from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.vit_lib import (
    repo_init_clone,
    asset_template,
    fetch
)


class TestAssetTemplate(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_local_path_1 = "tests/local_repo1"
    test_local_path_2 = "tests/local_repo2"
    template_file_path = "tests/test_data/mod_template.ma"
    template_checkout = "mod_template.ma"

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

    def test_create_asset_template(self):

        asset_template.create_asset_template(
            self.test_local_path_1,
            "mod", self.template_file_path
        )

        template_checkout = os.path.join(self.test_local_path_1, self.template_checkout)
        self.assertEqual(
            template_checkout,
            asset_template.get_template(self.test_local_path_1, "mod")
        )
        self.assertTrue(os.path.exists(template_checkout))

        template_checkout = os.path.join(self.test_local_path_2, self.template_checkout)
        self.assertEqual(
            template_checkout,
            asset_template.get_template(self.test_local_path_2, "mod")
        )
        self.assertTrue(os.path.exists(template_checkout))

    def test_list_templates(self):

        asset_template.create_asset_template(
            self.test_local_path_1,
            "mod_1", self.template_file_path
        )

        asset_template.create_asset_template(
            self.test_local_path_1,
            "mod_2", self.template_file_path
        )

        with ssh_connect_auto(self.test_local_path_2) as vit_connection:
            fetch.fetch(self.test_local_path_2, vit_connection)

        self.assertDictEqual(
            {'mod_1': 'mod_template.ma', 'mod_2': 'mod_template.ma'},
            asset_template.list_templates(self.test_local_path_2)
        )

    def test_create_asset_template_but_already_exists(self):
        asset_template.create_asset_template(
            self.test_local_path_1,
            "mod", self.template_file_path
        )
        with self.assertRaises(Template_AlreadyExists_E):
            asset_template.create_asset_template(
                self. test_local_path_1,
                "mod", self.template_file_path
            )
    def test_create_asset_template_already_exists_and_force_it(self):
        asset_template.create_asset_template(
            self.test_local_path_1,
            "mod", self.template_file_path
        )
        asset_template.create_asset_template(
            self.test_local_path_1,
            "mod", self.template_file_path,
            force=True
        )

    def test_create_asset_template_but_file_does_not_exists(self):
        with self.assertRaises(Path_FileNotFound_E):
            asset_template.create_asset_template(
                self. test_local_path_1,
                "mod", "path/that/does/not/exists"
            )

    def test_create_asset_template_but_template_does_not_exists(self):
        with self.assertRaises(Path_FileNotFound_E):
            asset_template.create_asset_template(
                self.test_local_path_1,
                "mod", "path/that/does/not/exists"
            )
        with self.assertRaises(Template_NotFound_E):
            asset_template.get_template(self.test_local_path_1, "template_not_found")


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
