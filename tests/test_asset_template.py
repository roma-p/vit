import os
import unittest

from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.vit_lib import (asset_template, fetch)
from tests import vit_test_repo as repo


class TestAssetTemplate(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_empty")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_create_asset_template(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset_template.create_asset_template(
                repo.test_local_path_1,
                vit_connection,
                repo.template_id,
                repo.template_file_path,
            )
            template_checkout = os.path.join(
                repo.test_local_path_1,
                repo.template_checkout
            )
            self.assertEqual(
                template_checkout,
                asset_template.get_template(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.template_id
                )
            )
            self.assertTrue(os.path.exists(template_checkout))

        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            template_checkout = os.path.join(
                repo.test_local_path_2,
                repo.template_checkout
            )
            self.assertEqual(
                template_checkout,
                asset_template.get_template(
                    repo.test_local_path_2,
                    vit_connection,
                    repo.template_id
                )
            )
            self.assertTrue(os.path.exists(template_checkout))

    def test_list_templates(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset_template.create_asset_template(
                repo.test_local_path_1,
                vit_connection,
                "mod_1", repo.template_file_path
            )

            asset_template.create_asset_template(
                repo.test_local_path_1,
                vit_connection,
                "mod_2", repo.template_file_path
            )

        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            fetch.fetch(repo.test_local_path_2, vit_connection)

        self.assertDictEqual(
            {
                'mod_1': 'mod_template.ma',
                'mod_2': 'mod_template.ma',
            },
            asset_template.list_templates(repo.test_local_path_2)
        )

    def test_create_asset_template_but_already_exists(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset_template.create_asset_template(
                repo.test_local_path_1,
                vit_connection,
                repo.template_id,
                repo.template_file_path,
            )
            with self.assertRaises(Template_AlreadyExists_E):
                asset_template.create_asset_template(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.template_id,
                    repo.template_file_path
                )

    def test_create_asset_template_already_exists_and_force_it(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset_template.create_asset_template(
                repo.test_local_path_1,
                vit_connection,
                repo.template_id,
                repo.template_file_path,
            )
            asset_template.create_asset_template(
                repo.test_local_path_1,
                vit_connection,
                repo.template_id,
                repo.template_file_path,
                force=True
            )

    def test_create_asset_template_but_file_does_not_exists(self):
        with self.assertRaises(Path_FileNotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                asset_template.create_asset_template(
                    repo.test_local_path_1,
                    vit_connection,
                    "new_template",
                    "path/that/does/not/exists"
                )

    def test_create_asset_template_but_template_does_not_exists(self):
        with self.assertRaises(Template_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                asset_template.get_template(
                    repo.test_local_path_1,
                    vit_connection,
                    "template_not_found"
                )


if __name__ == '__main__':
    unittest.main()
