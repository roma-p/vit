from vit.vit_lib.misc import tree_fetch
from vit.connection.vit_connection import ssh_connect_auto

def get_log_data(local_path, package_path, asset_name):
    tree_data = _get_tree_data(local_path, package_path, asset_name)
    log_data = {}

    def find_free_date(date):
        while True:
            if date in log_data:
                date += 1
            else:
                break
        return date

    for k, v in tree_data["commits"].items():
        date = find_free_date(v["date"])
        log_data[date] = {
            "commit": k,
            "user": v["user"],
            "message": v["message"]
        }
    for k, v in tree_data["tags"].items():
        if isinstance(v, str):
            date = find_free_date(tree_data["commits"][v]["date"])
            log_data[date] = {
                "tag": k,
                "commit": v
            }
        else:
            date = find_free_date(v["date"])
            log_data[date] = {
                "tag": k,
                "commit": v["parent"],
                "user": v["user"],
                "message": v["message"]
            }
    return log_data


def _get_tree_data(local_path, package_path, asset_name):
    with ssh_connect_auto(local_path) as ssh_connection:
        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path, asset_name)
        with tree_asset:
            tree_data = tree_asset.data
    return tree_data


