
def get_files_to_clean(local_path):

    _, _, user = repo_config.get_origin_ssh_info(local_path)

    file_to_clean = []
    file_editable = []
    file_non_editable_but_changed = []

    with IndexTrackedFile(path) as index_tracked_file:
        all_track_data = index_tracked_file.get_files_data(path)

    with ssh_connect_auto(local_path) as ssh_connection:
        for checkout_file, track_data in all_track_data:
            if check_is_file_editable(
                    ssh_connection,
                    local_path,
                    track_data["package_path"],
                    track_data["asset_name"],
                    track_data["origin_file_name"],
                    user):
                if track_data["changes"]:
                    file_non_editable_but_changed.append(checkout_file)
                else:
                    file_to_clean.append(checkout_file)
            else:
                file_editable.append(checkout_file)
    return {
        "to_clean": file_to_clean,
        "editable": file_editable,
        "changes": file_non_editable_but_changed
    }


def clean_files(local_path, file_list):
    with IndexTrackedFile(local_path) as index_tracked_file:
        for file in file_list:
            index_tracked_file.remove_file(file)
            os.remove(path_helpers.localize_path(local_path, file))


# -----------------------------------------------------------------------------


def check_is_file_editable(
        ssh_connection, package_path,
        asset_name, origin_file_name, user):
    tree_asset, tree_asset_path = fetch_tree.fetch_up_to_date_tree_asset(
            ssh_connection,
            local_path,
            file_track_data["package_path"],
            file_track_data["asset_name"]
    )
    return tree_asset.get_editor(file_track_data["origin_file_name"]) != user
