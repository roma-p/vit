import unittest

from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.vit_lib import (asset, fetch)

from tests import vit_test_repo as repo


class TestAsset(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo()

    def tearDown(self):
        repo.dispose_test_repo()

    def test_create_asset(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset.create_asset_from_template(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                "asset_1",
                repo.template_id
            )

            asset.create_asset_from_template(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                "asset_2",
                repo.template_id
            )

        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            fetch.fetch(repo.test_local_path_1, vit_connection)
        self.assertSetEqual(
            {"asset_1", "asset_2"},
            set(asset.list_assets(
                repo.test_local_path_1,
                repo.package_ok
            ))
        )

        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            fetch.fetch(repo.test_local_path_2, vit_connection)
        self.assertSetEqual(
            {"asset_1", "asset_2"},
            set(asset.list_assets(
                repo.test_local_path_2,
                repo.package_ok
            ))
        )

    def test_create_asset_but_template_not_found(self):
        with self.assertRaises(Template_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                asset.create_asset_from_template(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    "asset_1",
                    "non_existing_template"
                )

    def test_create_asset_but_package_not_found(self):
        with self.assertRaises(Package_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                asset.create_asset_from_template(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ko,
                    "asset_1",
                    repo.template_id
                )

    def test_create_asset_but_asset_already_exists(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset.create_asset_from_template(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                "asset_1",
                repo.template_id
                )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            with self.assertRaises(Asset_AlreadyExists_E):
                asset.create_asset_from_template(
                    repo.test_local_path_2,
                    vit_connection,
                    repo.package_ok,
                    "asset_1",
                    repo.template_id
                )

    def test_create_asset_from_file(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset.create_asset_from_file(
                repo.test_local_path_1,
                vit_connection,
                repo.package_ok,
                "asset_1",
                repo.template_file_path
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            fetch.fetch(repo.test_local_path_2, vit_connection)
        self.assertSetEqual(
            {"asset_1"},
            set(asset.list_assets(
                repo.test_local_path_2,
                repo.package_ok
            ))
        )

    def test_create_asset_from_file_but_file_not_found(self):
        with self.assertRaises(Path_FileNotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                asset.create_asset_from_file(
                    repo.test_local_path_1,
                    vit_connection,
                    repo.package_ok,
                    "asset_1",
                    "file_not_found.ma"
                )


if __name__ == '__main__':
    unittest.main()
