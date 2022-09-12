from vit import constants
from vit.custom_exceptions import *
from vit.vit_lib import (
    asset_template, asset, branch, checkout,
    clean, commit, display_info, package,
    repo_init_clone, tag
)

import logging
log = logging.getLogger()
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


def create_template(template_name, file_path, force=False):
    if not is_vit_repo(): return False
    try:
        asset_template.create_template_asset(
            os.getcwd(),
            template_name,
            file_path,
            force
        )
    except (
            Path_FileNotFound_E,
            SSH_ConnectionError_E,
            Template_AlreadyExists_E) as e:
        log.error("Could not create template {} from {}".format(
            template_name,
            file_path
        ))
        log.error(str(e))
        return False
    else:
        log.info("template {} successfully created from file {}".format(
            template_name,
            file_path))
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
            Path_AlreadyExists_E,
            Path_ParentDirNotExist_E) as e:
        log.error("Could not create package {}".format(path))
        log.error(str(e))
        return False
    else:
        log.info("package successfully created at {}".format(path))
        return True


def create_asset(package, asset_name, template):
    if not is_vit_repo(): return False
    try:
        asset.create_asset(
            os.getcwd(),
            package, asset_name, template
        )
    except (
            SSH_ConnectionError_E,
            Package_NotFound_E,
            Path_AlreadyExists_E,
            Template_NotFound_E) as e:
        log.error("plus tard")
        log.error(str(e))
        return False
    else:
        log.info("asset {} successfully created at {}".format(
            asset, package))
        return True


def checkout_asset_by_branch(package, asset, branch, editable, reset):
    if not is_vit_repo(): return False
    try:
        checkout_file = checkout.checkout_asset_by_branch(
            os.getcwd(),
            package,
            asset,
            branch,
            editable,
            reset
        )
    except (
            SSH_ConnectionError_E,
            Package_NotFound_E,
            Branch_NotFound_E,
            Asset_AlreadyEdited_E,
            Asset_NotFound_E) as e:
        log.error("plustard")
        log.error(str(e))
        return False
    else:
        log.info("asset {} successfully checkout at {}".format(
            asset, checkout_file))
        return True


def commit(file, message, keep_file, keep_editable):
    # FIXME: handle multiple commits at once?
    #   (and ask for confirmation).
    err = "Could not commit file {}".format(file)
    if not is_vit_repo(): return False
    try:
        commit.commit_file(
            os.getcwd(), file, message,
            keep_file, keep_editable
        )
    except Asset_NotEditable_E as e:
        log.error(err)
        log.error(str(e))
        log.info("* you can try to fetch it as editable so you can commit it")
        log.info("    following line won't overwrite your local modification")
        log.info("    vit fetch {} -e".format(file))
        log.info("* you can also create a new branch from you local file")
        log.info("    vit branch <branch name>  --from-file {}".format(file))
        return False
    except (
            Asset_NotFound_E,
            Asset_UntrackedFile_E,
            Asset_NoChangeToCommit_E,
            Asset_NotAtTipOfBranch,
            SSH_ConnectionError_E) as e:
        log.error(err)
        log.error(str(e))
        return False
    else:
        log.info("file {} successfully committed".format(file))
        return True


def create_branch_from_origin_branch(package, asset, branch_new, branch_parent):
    if not is_vit_repo(): return False
    try:
        branch.branch_from_origin_branch(
            os.getcwd(),
            package,
            asset,
            branch_parent,
            branch_new
        )
    except (
            SSH_ConnectionError_E,
            Asset_NotFound_E,
            Branch_NotFound_E,
            Branch_AlreadyExist_E) as e:
        log.error("plustard")
        log.error(str(e))
        return False
    else:
        log.info("pareil plus tard.")
        return True


def create_tag_light_from_branch(package, asset, branch, tag_name):
    if not is_vit_repo(): return False
    try:
        tag.create_tag_light_from_branch(
            os.getcwd(),
            package,
            asset,
            branch,
            tag_name
        )
    except (
            SSH_ConnectionError_E,
            Asset_NotFound_E,
            Branch_NotFound_E,
            Tag_AlreadyExists_E) as e:
        log.error("Could not tag create {} for asset {}".format(
            tag_name, asset
        ))
        log.error(str(e))
        return False
    else:
        log.info("Successfully tagged {} {} to {} from {}".format(
            package, asset,
            tag_name, branch
        ))
        return True


def list_templates():
    if not is_vit_repo(): return False
    try:
        template_data = display_info.list_templates(os.getcwd())
    except SSH_ConnectionError_E as e:
        log.error("Could not list templates.")
        log.error(str(e))
        return False
    else:
        log.info("templates found on origin repository are:")
        for template_id, template_file in template_data.items():
            log.info("    - {} : {}".format(template_id, template_file))
        return True


def get_template(template_id):
    if not is_vit_repo(): return False
    try:
        template_path_local = display_info.get_template(os.getcwd(), template_id)
    except (
            SSH_ConnectionError_E,
            Template_NotFound_E) as e:
        log.error("Could not get template file for {}".format(template_id))
        log.error(str(e))
        return False
    else:
        log.info("template {} successfully copied at: {}".format(
            template_id,
            template_path_local
        ))
        return True


def list_packages():
    if not is_vit_repo(): return False
    try:
        packages = display_info.list_packages(os.getcwd())
    except SSH_ConnectionError_E as e:
        log.error("Could not list templates.")
        log.error(str(e))
        return False
    else:
        log.info("packages found on origin repository are:")
        for package in packages:
            log.info("    - {}".format(package))
        return True


def list_assets(package):
    if not is_vit_repo(): return False
    try:
        assets = display_info.list_assets(os.getcwd(), package)
    except (
            SSH_ConnectionError_E,
            Package_NotFound_E) as e:
        log.error("Could not list assets for package {}.".format(package))
        log.error(str(e))
        return False
    else:
        log.info("Assets found on origin for package {} repository are:".format(
            package))
        for asset in assets:
            log.info("    - {}".format(asset))
        return True


def list_branches(package, asset):
    if not is_vit_repo(): return False
    try:
        branches = display_info.list_branches(os.getcwd(), package, asset)
    except (
            SSH_ConnectionError_E,
            Package_NotFound_E,
            Asset_NotFound_E) as e:
        log.error("Could not list branches for assets {} {}.".format(package, asset))
        log.error(str(e))
        return False
    else:
        log.info("branches of {} {}".format(package, asset))
        for branch in branches:
            log.info("    - {}".format(branch))
        return True


def list_tags(package, asset):
    if not is_vit_repo(): return False
    try:
        tags = display_info.list_tags(os.getcwd(), package, asset)
    except (
            SSH_ConnectionError_E,
            Package_NotFound_E,
            Asset_NotFound_E) as e:
        log.error("Could not list tags for assets {} {}.".format(package, asset))
        log.error(str(e))
        return False
    else:
        log.info("tags of {} {}".format(package, asset))
        for tag in tags:
            log.info("    - {}".format(tag))
        return True

def info(file_ref):
    if not is_vit_repo(): return False
    try:
        data = display_info.get_info_from_ref_file(os.getcwd(), file_ref)
    except (
            SSH_ConnectionError_E,
            Path_FileNotFound_E,
            Asset_UntrackedFile_E) as e:
        log.error("Could not get info for file: ".format(file_ref))
        log.error(str(e))
        return False
    else:
        log.info(file_ref)
        log.info("\t{}: {} -> {}".format(
            data["asset_name"],
            data["checkout_type"],
            data["checkout_value"]
        ))
        log.info("\tpackage: {}".format(data["package_path"]))
        log.info ("\teditable: {}".format(data["editable"]))
        log.info("\tchanges: {}".format(data["changes"]))
        return True
