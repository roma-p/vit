import os

class VitCustomException(Exception): pass

class VitCustomException_FetchNeeded(VitCustomException): pass

# PATH HANDLING --------------------------------------------------------------

class Path_ParentDirNotExist_E(VitCustomException):
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return "parent directory of {} does not exists.".format(self.path)

class Path_AlreadyExists_E(VitCustomException):
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return "{} already exists.".format(self.path)

class Path_FileNotFound_E(VitCustomException):
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return "file {} not found.".format(self.path)

class Path_FileNotFoundAtOrigin_E(VitCustomException):
    def __init__(self, path, ssh_link):
        self.path = path
        self.ssh_link = ssh_link
    def __str__(self):
        return "required file {} not found at origin {}, maybe it has been deleted?".format(
            self.path,
            self.ssh_link)

# SSH HANDLING --------------------------------------------------------------

class SSH_ConnectionError_E(VitCustomException):

    def __init__(self, ssh_link, paramiko_exception):
        self.ssh_link = ssh_link
        self.exception = paramiko_exception

    def __str__(self):
        return "ssh error connecting to {}: {}".format(
            self.ssh_link,
            str(self.exception)
        )

class OriginNotFound_E(VitCustomException):
    def __init__(self, ssh_link):
        self.ssh_link = ssh_link
    def __str__(self):
        return "no repository found at {}.".format(self.ssh_link)

class RepoIsLock_E(VitCustomException):
    def __init__(self, ssh_link):
        self.ssh_link = ssh_link
    def __str__(self):
        return "repository is currently updated by someone else. " \
                "Try in a few seconds.".format(self.ssh_link)

# TEMPLATE -------------------------------------------------------------------

class Template_AlreadyExists_E(VitCustomException):
    def __init__(self, template_id):
        self.template_id = template_id
    def __str__(self):
        return "already a template named {}.".format(self.template_id)

class Template_NotFound_E(VitCustomException):
    def __init__(self, template_id):
        self.template_id = template_id
    def __str__(self):
        return "template not found: {}.".format(self.template_id)

# PACKAGE -------------------------------------------------------------------

class Package_NotFound_E(VitCustomException_FetchNeeded):
    def __init__(self, package):
        self.package = package
    def __str__(self):
        return "package not found: {}.".format(self.package)

class Package_AlreadyExists_E(VitCustomException):
    def __init__(self, package):
        self.package = package
    def __str__(self):
        return "already a package named {}.".format(self.package)


# ASSET ----------------------------------------------------------------------

class Asset_NotFound_E(VitCustomException_FetchNeeded):
    def __init__(self, package, asset):
        self.asset = asset
        self.package = package
    def __str__(self):
        return "asset not found: {}.".format(
            os.path.join(self.package, self.asset)
        )

class Asset_AlreadyExists_E(VitCustomException):
    def __init__(self, package, asset):
        self.asset = asset
        self.package = package
    def __str__(self):
        return "package {} already have an asset called {}.".format(
            self.package, self.asset
        )

class Asset_AlreadyEdited_E(VitCustomException):
    def __init__(self, asset, current_editor):
        self.asset = asset
        self.current_editor = current_editor
    def __str__(self):
        return "can't be editor of asset {}, currently already edited by: {}.".format(
            self.asset,
            self.current_editor)

class Asset_UntrackedFile_E(VitCustomException):
    def __init__(self, file):
        self.file = file
    def __str__(self):
        return "file {} is not tracked, it don't belong to the project.".format(
            self.file
        )

class Asset_NotEditable_E(VitCustomException):
    def __init__(self, asset):
        self.asset = asset
    def __str__(self):
        return "asset {} is not editable.".format(self.asset)

class Asset_NoChangeToCommit_E(VitCustomException):
    def __init__(self, asset):
        self.asset = asset
    def __str__(self):
        return "no change to commit for asset {}.".format(self.asset)

class Asset_ChangeNotCommitted_E(VitCustomException):
    def __init__(self, asset):
        self.asset = asset
    def __str__(self):
        return " uncommitted change on asset {}.".format(self.asset)

class Asset_NotAtTipOfBranch_E(VitCustomException):
    def __init__(self, asset, branch):
        self.asset  = asset
        self.branch = branch
    def __str__(self):
        return "can't commit asset {} as it is not at the tip of the branch {}".format(
            self.asset,
            self.branch
        )

class Asset_UpdateOnNonBranchCheckout_E(VitCustomException):
    def __init__(self, checkout_type):
        self.checkout_type = checkout_type
    def __str__(self):
        return "can only update checkout on 'branch' checkout, not on {} checkout".format(
            self.checkout_type
        )

class Asset_AlreadyUpToDate_E(VitCustomException):
    def __init__(self, asset):
        self.asset = asset
    def __str__(self):
        return "asset {} already up to date.".format(self.asset)

# BRANCH ----------------------------------------------------------------------

class Branch_NotFound_E(VitCustomException_FetchNeeded):
    def __init__(self, asset, branch):
        self.branch = branch
        self.asset = asset
    def __str__(self):
        return "branch {} not found for asset {}".format(
           self.branch,
           self.asset
        )

class Branch_AlreadyExist_E(VitCustomException):
    def __init__(self,asset, branch):
        self.branch = branch
        self.asset = asset
    def __str__(self):
        return "there already is a branch named {} on asset {}".format(
            self.branch,
            self.asset
        )

# TAG ------------------------------------------------------------------------

class Tag_AlreadyExists_E(VitCustomException):
    def __init__(self,asset, tag):
        self.tag = tag
        self.asset = asset
    def __str__(self):
        return "there already is a tag named {} on asset {}".format(
            self.tag,
            self.asset
        )

class Tag_NotFound_E(VitCustomException_FetchNeeded):
    def __init__(self, asset, tag):
        self.tag = tag
        self.asset = asset
    def __str__(self):
        return "tag {} not found for asset {}".format(
           self.tag,
           self.asset
        )

class Tag_NameMatchVersionnedTag_E(VitCustomException):
    def __init__(self, tag):
        self.tag = tag
    def __str__(self):
        ret = "tag name {} match versionned tag format.".format(self.tag)
        "Create a versionned tag instead."
        return ret

# COMMIT -----------------------------------------------------------------------

class Commit_NotFound_E(VitCustomException):
    def __init__(self, asset, commit):
        self.commit = commit
        self.asset = asset
    def __str__(self):
        return "commit {} not found for asset {}".format(
           self.commit,
           self.asset
        )

