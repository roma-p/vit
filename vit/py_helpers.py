import os
import json
import socket
import subprocess

def write_json(json_file_path, data): 
    if not os.path.exists(os.path.dirname(json_file_path)):
        return False
    with open(json_file_path, "w") as outfile:
        json.dump(json_file_path, outfile)

def get_hostname():
    return socket.gethostname()

