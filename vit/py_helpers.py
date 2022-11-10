import os
import json
import hashlib

# Dealing with json files -----------------------------------------------------


def write_json(json_file_path, data):
    if not os.path.exists(os.path.dirname(json_file_path)):
        return False
    with open(json_file_path, "w") as f:
        json.dump(data, f, indent=4)
    return True


def update_json(json_file_path, data):
    if not os.path.exists(os.path.dirname(json_file_path)):
        return False
    with open(json_file_path, "r") as f:
        current_data = json.load(f)
    current_data.update(data)
    with open(json_file_path, "w") as f:
        json.dump(current_data, f, indent=4)
    return True


def create_empty_json(path):
    return write_json(path, {})


def get_json_main_key(json_file_path, key):
    with open(json_file_path, "r") as f:
        data = json.load(f)
    return data.get(key, None)


# misc ------------------------------------------------------------------------


def calculate_file_sha(filepath):
    with open(filepath, "rb") as f:
        b = f.read()
        readable_hash = hashlib.sha256(b).hexdigest()
    return readable_hash


def get_current_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_file_extension(file_path):
    _, extension = os.path.splitext(file_path)
    return extension

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
