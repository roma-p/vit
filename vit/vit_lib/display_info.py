from vit import path_helpers
from vit.connection.vit_connection import ssh_connect_auto
from vit.custom_exceptions import *
from vit.file_handlers.index_tracked_file import IndexTrackedFile
from vit.file_handlers.tree_asset import TreeAsset


def get_info_from_ref_file(path, ref_file):
    ref_file_local = path_helpers.localize_path(path, ref_file)
    if not os.path.exists(ref_file_local):
        raise Path_FileNotFound_E(ref_file_local)
    with IndexTrackedFile(path) as index_tracked_file:
        file_data = index_tracked_file.get_files_data(path)
    if ref_file not in file_data:
        raise Asset_UntrackedFile_E(ref_file)
    return file_data[ref_file]
    # TODO editable information not here... Needs refacto.
