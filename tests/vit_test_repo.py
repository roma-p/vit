import os
import shutil

from vit.connection.vit_connection import ssh_connect_auto
from vit.connection.vit_connection import VitConnection
from vit.vit_lib import (
    repo_init_clone,
    package, asset,
    asset_template,
)

from vit.connection.ssh_connection import SSHConnection
from tests.fake_ssh_connection import FakeSSHConnection

test_origin_path_ok = "tests/origin_repo"
test_local_path_1 = "tests/local_repo1"
test_local_path_2 = "tests/local_repo2"

package_ok = "the/package"
package_ko = "the/package/nupe"

template_id = "mod"
template_checkout = "mod_template.ma"
template_file_path = "tests/test_data/mod_template.ma"


def setup_test_repo():
    VitConnection.SSHConnection = FakeSSHConnection
    _clean_dir()
    _init_repos()


def dispose_test_repo():
    VitConnection.SSHConnection = SSHConnection
    _clean_dir()


def _init_repos():
    repo_init_clone.init_origin(test_origin_path_ok)

    # cloning origin on repo1
    _clone(test_local_path_1, test_origin_path_ok, "romainpelle", "localhost")
    _clone(test_local_path_2, test_origin_path_ok, "romainpelle", "localhost")

    with ssh_connect_auto(test_local_path_1) as vit_connection:
        asset_template.create_asset_template(
            test_local_path_1,
            vit_connection,
            template_id,
            template_file_path
        )
        package.create_package(
            test_local_path_1,
            vit_connection,
            package_ok,
            force_subtree=True
        )


def _clone(clone_path, origin_path, user, host):
    origin_path_abs = os.path.abspath(origin_path)
    vit_connection = VitConnection(
        clone_path, host,
        origin_path_abs, user
    )
    with vit_connection:
        repo_init_clone.clone(
            vit_connection,
            origin_path_abs,
            clone_path,
            user, host
        )


def _clean_dir():
    for path in (
            test_origin_path_ok,
            test_local_path_1,
            test_local_path_2):
        _rm_dir(path)


def _rm_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)
