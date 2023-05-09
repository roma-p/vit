import unittest

from vit.custom_exceptions import *
from vit.vit_lib import (asset_template, package, asset, fetch)

from tests import vit_test_repo as repo
from vit.connection.connection_utils import ssh_connect_auto


class TestFetch(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_empty")
        self._init_repos()

    def tearDown(self):
        repo.dispose_test_repo()

    def test_fetch(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            fetch.fetch(vit_connection)

    def test_get_repo_hierarchy(self):

        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            fetch.fetch(vit_connection)

        result = fetch.get_repo_hierarchy(repo.test_local_path_1)
        expected = {
            'package1': {
                'packages': {
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
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            fetch.fetch(vit_connection)
        result = fetch.get_all_assets_info(repo.test_local_path_1)

    def _init_repos(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            asset_template.create_asset_template(
                vit_connection,
                repo.template_id,
                repo.template_file_path
            )
            package.create_package(
                vit_connection,
                "package1",
                force_subtree=True
            )
            package.create_package(
                vit_connection,
                "package2",
                force_subtree=True
            )
            package.create_package(
                vit_connection,
                "package1/subpackage1",
                force_subtree=True
            )
            package.create_package(
                vit_connection,
                "package1/subpackage2",
                force_subtree=True
            )
            asset.create_asset_from_template(
                vit_connection,
                "package1",
                "asset1",
                repo.template_id
            )

            asset.create_asset_from_template(
                vit_connection,
                "package1/subpackage1",
                "asset2",
                repo.template_id
            )

            asset.create_asset_from_template(
                vit_connection,
                "package1/subpackage1",
                "asset3",
                repo.template_id
            )

            asset.create_asset_from_template(
                vit_connection,
                "package2",
                "asset4",
                repo.template_id
            )


if __name__ == '__main__':
    unittest.main()
