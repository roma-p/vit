import json

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

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            self.update_data()

    @staticmethod
    def file_read(func):
        def wrapper(self, *args, **kargs):
            if self.data is None:
                raise JsonFileDataAccessedBeforeRead(self.path)
            return func(self, *args, **kargs)
        return wrapper

class JsonFileDataAccessedBeforeRead(Exception):
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return "Json file {} data accessed before file was read.".format(self.path)