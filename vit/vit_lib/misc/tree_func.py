from vit.custom_exceptions import *


def become_editor_of_asset(tree_asset, asset_name, asset_filepath, user):
    editor = tree_asset.get_editor(asset_filepath)
    if editor and editor != user:
        raise Asset_AlreadyEdited_E(asset_name, editor)
    tree_asset.set_editor(asset_filepath, user)


