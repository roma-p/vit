import json

import logging
log = logging.getLogger()


class JsonFile(object):

    def __init__(self, path):
        self.path = path
        self.data = None

    def read_file(self):
        with open(self.path, "r") as f:
            self.data = json.load(f)

    def update_data(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def __enter__(self):
        self.read_file()
        return self

    def __exit__(self, t, value, traceback):
        self.update_data()

    @staticmethod
    def file_read(func):
        def wrapper(self, *args, **kargs):
            if self.data is None:
                log.error("file not reade can't access its data.")
                return
            return func(self, *args, **kargs)
        return wrapper
