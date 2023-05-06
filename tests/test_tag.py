import time
import unittest

from vit.custom_exceptions import *
from vit.vit_lib import (tag, branch, fetch)

from tests import vit_test_repo as repo
from vit.connection.vit_connection import ssh_connect_auto


class TestTag(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    def test_create_tag_light_from_branch(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            tag.create_tag_light_from_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                "my_tag_1"
            )
            tag.create_tag_light_from_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                "my_tag_2"
            )
        with ssh_connect_auto(repo.test_local_path_2) as ssh_connection:
            fetch.fetch(ssh_connection)
        self.assertSetEqual(
            {"my_tag_1", "my_tag_2"},
            set(tag.list_tags(
                repo.test_local_path_2,
                repo.package_ok,
                repo.asset_ok
            ))
        )

    def test_create_tag_light_from_branch_not_found(self):
        with self.assertRaises(Branch_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                tag.create_tag_light_from_branch(
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "branch_not_found",
                    "my_tag_1"
                )

    def test_create_tag_light_from_branch_but_tag_already_exists(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            tag.create_tag_light_from_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base",
                "my_tag_1"
            )
            with self.assertRaises(Tag_AlreadyExists_E):
                tag.create_tag_light_from_branch(
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base",
                    "my_tag_1"
                )

    def test_create_annotated_tag_from_branch(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            tag.create_tag_annotated_from_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "base", "my_tag_1",
                "hello world this is my commit message"
            )
        with ssh_connect_auto(repo.test_local_path_2) as ssh_connection:
            fetch.fetch(ssh_connection)
        self.assertEqual(
            ("my_tag_1",),
            tag.list_tags(
                repo.test_local_path_2,
                repo.package_ok,
                repo.asset_ok
            )
        )

    def test_create_annotated_tag_from_branch_but_branch_not_found(self):
        with self.assertRaises(Branch_NotFound_E):
            with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
                tag.create_tag_annotated_from_branch(
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "branch_not_found", "my_tag_1",
                    "hello world this is my commit message"
                )

    def test_auto_tag(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            tag.create_tag_auto_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", "message", 1
            )
            tag.create_tag_auto_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", "message", 2
            )
            tag.create_tag_auto_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", "message", 2
            )
            tag.create_tag_auto_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", "message", 0
            )

        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            fetch.fetch(vit_connection)
        self.assertSetEqual(
            {
                'asset_ok-base-v0.1.0',
                'asset_ok-base-v0.1.1',
                'asset_ok-base-v0.1.2',
                'asset_ok-base-v1.0.0'
            },
            set(tag.list_tags(
                repo.test_local_path_2,
                repo.package_ok,
                repo.asset_ok
            ))
        )

    def test_list_auto_tag_by_branch(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            branch.create_branch(
                vit_connection,
                repo.package_ok,
                repo.asset_ok,
                "new_branch", branch_parent="base")
            tag.create_tag_auto_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "base", "message", 1
            )
            tag.create_tag_auto_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "new_branch", "message", 1
            )
            tag.create_tag_annotated_from_branch(
                vit_connection,
                repo.package_ok, repo.asset_ok,
                "new_branch", "new_taaaag", "message"
            )
        with ssh_connect_auto(repo.test_local_path_2) as vit_connection:
            fetch.fetch(vit_connection)
        self.assertEqual(
            ("asset_ok-new_branch-v0.1.0",),
            tag.list_auto_tags_by_branch(
                repo.test_local_path_2,
                repo.package_ok,
                repo.asset_ok,
                "new_branch"
            )
        )
        self.assertEqual(
            ("asset_ok-base-v0.1.0",),
            tag.list_auto_tags_by_branch(
                repo.test_local_path_2,
                repo.package_ok,
                repo.asset_ok,
                "base"
            )
        )

    def test_non_auto_tags_conflict_with_auto_tag(self):
        with ssh_connect_auto(repo.test_local_path_1) as vit_connection:
            with self.assertRaises(Tag_NameMatchVersionnedTag_E):
                tag.create_tag_light_from_branch(
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base",
                    "asset_ok-base-v0.6.3"
                )
            with self.assertRaises(Tag_NameMatchVersionnedTag_E):
                tag.create_tag_annotated_from_branch(
                    vit_connection,
                    repo.package_ok,
                    repo.asset_ok,
                    "base",
                    "asset_ok-base-v0.4.2",
                    "tamerelapute"
                )

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
