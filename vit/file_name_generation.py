
def generate_unique_asset_file_name(asset_name, extension):
    return "{}-{}{}".format(asset_name, uuid.uuid4(), extension)

def generate_checkout_path(
        origin_file_path, package_path,
        asset_name, suffix):
    extension = py_helpers.get_file_extension(origin_file_path)
    asset_name_local = generate_asset_file_name_local(
        asset_name,
        suffix,
        extension
    )
    asset_path = os.path.join(package_path, asset_name_local)
    return asset_path

def generate_checkout_file_name(asset_name, suffix, extension):
    return "{}-{}{}".format(asset_name, suffix, extension)
