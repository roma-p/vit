import os
import shutil
from vit.connection.vit_connection import VitConnection


class VitConnectionLocal(VitConnection):

    def __init__(self, local_path, server, origin_path, user):
        super().__init__(local_path, server, origin_path, user)
        self.host = "localhost"
        self.ssh_connection = self.SSHConnection(self.host, self.user)

    def get_data_from_origin(
            self, src, dst,
            recursive=False,
            is_editable=False):

        copy_func = shutil.copytree if recursive else shutil.copy

        src = self._format_path_origin(src)
        dst = self._format_path_local(dst)

        if os.path.exists(dst):
            if is_editable and os.path.islink(dst):
                os.remove(dst)
            elif not is_editable and not os.path.islink(dst):
                # TODO: DANGEROUS...
                os.remove(dst)

        if os.path.exists(dst) and os.path.islink(dst):
            os.remove(dst)

        if is_editable:
            return copy_func(src, dst)
        else:
            return os.symlink(src, dst)

    def put_data_to_origin(
            self, src, dst,
            recursive=False,
            is_src_abritrary_path=False):

        if is_src_abritrary_path:
            src = os.path.abspath(src)

        copy_func = shutil.copytree if recursive else shutil.copy

        return copy_func(
            self._format_path_local(src),
            self._format_path_origin(dst)
        )

    def put_commit_to_origin(
            self, src, dst,
            keep_file,
            keep_editable,
            recursive=False):

        src = self._format_path_local(src)
        dst = self._format_path_origin(dst)

        copy_func = shutil.copytree if recursive else shutil.copy
        copy_func(src, dst)

        if keep_editable and not keep_file:
            raise EOFError()
        elif keep_file and keep_editable:
            return
        elif keep_file and not keep_editable:
            os.remove(src)
            os.symlink(dst, src)
        else:
            os.remove(src)
