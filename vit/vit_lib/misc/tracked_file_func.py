from vit import path_helpers
from vit import py_helpers
from vit.custom_exceptions import *
from vit.file_handlers.index_tracked_file import IndexTrackedFile


def get_file_track_data(local_path, checkout_file):
    localized_path = os.path.join(local_path, checkout_file)
    if not os.path.exists(localized_path):
        raise Path_FileNotFound_E(localized_path)
    with IndexTrackedFile(local_path) as index_tracked_file:
        file_data = index_tracked_file.get_files_data(local_path)
    if checkout_file not in file_data:
        raise Asset_UntrackedFile_E(checkout_file)
    return file_data[checkout_file]


def remove_tracked_file(local_path, checkout_file):
    os.remove(path_helpers.localize_path(local_path, checkout_file))
    with IndexTrackedFile(local_path) as index_tracked_file:
        index_tracked_file.remove_file(checkout_file)


def update_tracked_file(
        local_path, checkout_file,
        new_original_file, update_sha=True):
    sha256 = py_helpers.calculate_file_sha(
        path_helpers.localize_path(local_path, checkout_file)
    )
    with IndexTrackedFile(local_path) as index_tracked_file:
        index_tracked_file.set_new_original_file(
            checkout_file,
            new_original_file
        )
        if update_sha:
            index_tracked_file.update_sha(checkout_file, sha256)
