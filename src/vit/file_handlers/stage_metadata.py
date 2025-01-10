import os


class StagedMetadata(object):

    def __init__(
            self,
            meta_data_file_path,
            stage_file_path,
            stage_file_path_local,
            file_handler_class):
        self.meta_data_file_path = meta_data_file_path
        self.stage_file_path = stage_file_path
        self.stage_file_path_local = stage_file_path_local
        self.file_handler = None
        self.file_handler = file_handler_class(self.stage_file_path_local)

    def __enter__(self):
        self.file_handler.read_file()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            self.file_handler.update_data()

    def remove_stage_metadata(self):
        os.remove(self.stage_file_path_local)
