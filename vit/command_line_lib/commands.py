from vit import constants
from vit.custom_exceptions import *
from vit.vit_lib import (
    asset_template,
    asset, branch, checkout,
    clean, commit, infos, package,
    repo_init_clone, tag, rebase, update
)
from vit.command_line_lib import graph as graph_module
from vit.command_line_lib import log as log_module

import logging
log = logging.getLogger("vit")
log.setLevel(logging.INFO)


def is_vit_repo():
    current_path = os.getcwd()
    s = os.path.exists(
        os.path.join(
            current_path,
            constants.VIT_DIR
        )
    )
    if not s:
        log.error("{} is not a vit repository".format(current_path))
    return s


def parse_ssh_link(link):
    if ":" not in link:
        return None
    split = link.split(":")
    if len(split) != 2:
        return None
    host, path = link.split(":")
    if "@" in host:
        split = host.split("@")
        if len(split) > 2:
            return None
        user, host = split
    else:
        user = input("username:")
    if not user or not host or not path:
        return None
    return user, host, path


def init(name):
    try:
        repo_init_clone.init_origin(
            os.path.join(
                os.getcwd(),
                name
            )
        )
    except (
            Path_AlreadyExists_E,
            Path_ParentDirNotExist_E,
            Exception) as e:
        log.error("Could not initialize repository {}:".format(name))
        log.error(str(e))
        return False
    else:
        log.info("Repository successfully initialized at {}".format(name))
        return True


def clone(origin_link):

    origin_link = parse_ssh_link(origin_link)
    if not origin_link:
        log.error("{} is not a valid ssh link")
        return False
    user, host, origin_path = origin_link

    repository_name = os.path.basename(origin_path)
    clone_path = os.path.join(
        os.getcwd(),
        repository_name
    )

    try:
        repo_init_clone.clone(origin_path, clone_path, user, host)
    except (
            Path_AlreadyExists_E,
            Path_ParentDirNotExist_E,
            SSH_ConnectionError_E,
            OriginNotFound_E) as e:
        log.error("Could not clone repository {}:".format(origin_link))
        log.error(str(e))
        return False
    else:
        log.info("{} successfully cloned at: {}".format(
            repository_name,
            clone_path
        ))
        return True


def create_package(path):
    if not is_vit_repo(): return False
    try:
        package.create_package(
            os.getcwd(),
            path,
            force_subtree=False
            # TODO: add option for this....
        )
    except (
            SSH_ConnectionError_E,
            RepoIsLock_E,
            Path_AlreadyExists_E,
            Path_ParentDirNotExist_E) as e:
        log.error("Could not create package {}".format(path))
        log.error(str(e))
        return False
    else:
        log.info("Package successfully created at {}".format(path))
        return True


def list_packages():
    if not is_vit_repo(): return False
    try:
        packages = package.list_packages(os.getcwd())
    except (SSH_ConnectionError_E,
            Package_NotFound_E) as e:
        log.error("Could not list templates.")
        log.error(str(e))
        return False
    else:
        if not packages:
            log.info("no package found on origin repository.")
        else:
            log.info("packages found on origin repository are:")
            for p in packages:
                log.info("    - {}".format(p))
        return True



