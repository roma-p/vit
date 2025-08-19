import os

def split_asset_path(asset_path):
    return (
        os.path.dirname(asset_path),
        os.path.basename(asset_path),
    )
