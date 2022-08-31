import os
import json
import socket
import subprocess
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

def parse_json(json_file_path):
    with open(json_file_path, "r") as f:
        data = json.load(f)
    return data

def override_json(json_file_path, data):
    if not os.path.exists(os.path.dirname(json_file_path)):
        return False
    with open(json_file_path, "r") as f:
        current_data = json.load(f)
    with open(json_file_path, "w") as f:
        json.dump(data, f, indent=4)

# misc ------------------------------------------------------------------------

def calculate_file_sha(filepath):
    with open(filepath,"rb") as f:
        bytes = f.read()
        readable_hash = hashlib.sha256(bytes).hexdigest();
    return readable_hash

def get_current_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_file_extension(file_path):
    _, extension = os.path.splitext(file_path)
    return extension
