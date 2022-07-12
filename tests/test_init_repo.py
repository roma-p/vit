import os
import shutil
import unittest

from context import vit
from vit import init_origin, init_local


class TestInitOriginRepo(unittest.TestCase):

    test_origin_path_ok = "tests/origin_repo"
    test_origin_path_ko = "nupes/origin_repo"
    test_local_path_ok = "tests/local_repo"
    test_local_path_ko = "nupes/local_repo"

    def setUp(self):
        self._clean_dir()

    def tearDown(self):
        self._clean_dir()

    def test_create_origin(self): 
        self.assertTrue(init_origin.init_origin(self.test_origin_path_ok))
        self.assertFalse(init_origin.init_origin(self.test_origin_path_ok)) # if already a vit dir.
        self.assertFalse(init_origin.init_origin(self.test_origin_path_ko))

        self.assertTrue(os.path.exists(self.test_origin_path_ok))
        self.assertTrue(os.path.exists(os.path.join(self.test_origin_path_ok, ".vit")))
        self.assertTrue(os.path.exists(os.path.join(self.test_origin_path_ok, ".vit/config.json")))

    def test_add_asset_container(self):

        container = "models"
        container_path = os.path.join(self.test_origin_path_ok, container)
        tasks = {
            "mod", 
            "rigg",
            "surf",
            "cfx"
        }

        self.assertTrue(init_origin.init_origin(self.test_origin_path_ok))
        self.assertTrue(init_origin.add_asset_container(self.test_origin_path_ok, container, *tasks))

        self.assertTrue(os.path.exists(container_path))
        for task in tasks: 
            self.assertTrue(os.path.exists(os.path.join(container_path, task)))

    def test_clone_basic(self): 
        self.assertTrue(init_origin.init_origin(self.test_origin_path_ok))
        self.assertTrue(init_local.clone(
            os.path.abspath(self.test_origin_path_ok),
            self.test_local_path_ok,
            "romainpelle", "localhost"
        ))

    def _clean_dir(self): 
        for path in (
                self.test_origin_path_ok,
                self.test_local_path_ok):
            self._rm_dir(path)        

    @staticmethod
    def _rm_dir(directory): 
        if os.path.exists(directory):
            shutil.rmtree(directory, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()