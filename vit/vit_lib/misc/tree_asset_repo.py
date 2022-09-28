from vit.connection.vit_connection import ssh_connect_auto
from vit.file_handlers.tree_asset import TreeAsset
from vit.vit_lib.misc import tree_fetch

class TreeAssetRepo(object):
    """
    class to abstract "modify asset" network / file access.
    -> on enter: will open a sshh connection, fetch the asset file tree and parse it.
    -> on exit: will update the asset tree file, uplaod it on origin and close ssh connection.
    """

    def __init__(self, local_path, package_path, asset_name):
        self.local_path = local_path
        self.package_path = package_path
        self.asset_name = asset_name

        self.tree_asset = None
        self.tree_asset_path = None
        self.ssh_connection = None

    def __enter__(self):
        print("11111111")
        self.ssh_connection = ssh_connect_auto(self.local_path)
        self.ssh_connection.open_connection()
        self.tree_asset, self.tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            self.ssh_connection, self.local_path,
            self.package_path, self.asset_name
        )
        self.tree_asset.read_file()
        print("2222222")
        return self

    def __exit__(self, t, value, traceback):
        print('ouiiiii')
        self.tree_asset.update_data()
        self.ssh_connection.put_auto(self.tree_asset_path, self.tree_asset_path)
        self.ssh_connection.close_connection()
        print("ouiiiiiii")
