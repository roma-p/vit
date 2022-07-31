import logging
log = logging.getLogger()

from vit import main_commands

def log_current_status(path):
    log_data = main_commands.get_status_local(path)
    print("status of local data:")
    print("")
    for package, d1 in log_data.items():
        print(package)
        for asset, d2 in d1.items():
            print("    - "+asset)
            for branch, d3 in d2.items():
                print("        * branch: "+branch)
                print("           file: "+d3["file"])
                print("           change to commit: "+str(d3["to_commit"]))
