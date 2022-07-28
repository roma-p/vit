import os
import json
import socket
import subprocess
import hashlib


# Dealing with raw files ------------------------------------------------------

def create_empty_file(filepath): 
    open(filepath, 'a').close()

def erase_file_content(filepath): 
    open(filepath, 'w').close()

def append_line_to_file(file, line): 
    with open(file, "a") as f:
        f.write(line+"\n")

def read_lines_from_file(file):
    with open(file, "r") as f:
        lines = f.read().splitlines()
    return lines

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

# misc ------------------------------------------------------------------------

def get_hostname():
    return socket.gethostname()

def calculate_file_sha(filepath): 
    with open(filepath,"rb") as f:
        bytes = f.read()
        readable_hash = hashlib.sha256(bytes).hexdigest();
    return readable_hash
