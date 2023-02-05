import unittest

from vit.custom_exceptions import *
from vit.vit_lib import infos


from tests import vit_test_repo as repo
from vit.connection.vit_connection import ssh_connect_auto


class TestInfos(unittest.TestCase):

    def setUp(self):
        repo.setup_test_repo("repo_base")

    def tearDown(self):
        repo.dispose_test_repo()

    @staticmethod
    def _append_line_to_file(file, line):
        with open(file, "a") as f:
            f.write(line)


if __name__ == '__main__':
    unittest.main()
