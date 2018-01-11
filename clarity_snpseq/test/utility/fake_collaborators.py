from __future__ import print_function
import StringIO
import os
from pyfakefs import fake_filesystem
from pyfakefs.fake_filesystem import FakeOsModule
from pyfakefs.fake_filesystem_shutil import FakeShutilModule
from pyfakefs.fake_filesystem import FakeFileOpen
from contextlib import contextmanager
from clarity_ext.service.file_service import FileService


class MockedUploadService:
    def __init__(self, file_service, os_service):
        self.call_stack = []
        self.file_service = file_service
        self.os_service = os_service
        self.local_shared_file_buffer = MockedStreamCatcher()

    def mock_upload_files(self, file_handle, files_with_name):
        self.call_stack.append((file_handle, files_with_name))

    def mock_upload_single(self, artifact, file_handle, instance_name, content, file_prefix):
        self.file_service.artifactid_by_filename[instance_name] = artifact.id
        files_with_name = [(instance_name, content)]
        self.call_stack.append((file_handle, files_with_name))

    def mock_local_shared_file(self, file_handle, mode='r', extension="", modify_attached=False,
                               file_name_contains=None):
        artifact = self.file_service._artifact_by_name(file_handle, file_name_contains)
        local_file_name = "{}_{}.{}".format(artifact.id, file_handle.replace(" ", "_"), extension)
        downloaded_path = os.path.join(self.file_service.downloaded_path, local_file_name)
        if not self.os_service.exists(downloaded_path):
            self.os_service.create_file(downloaded_path)
        if modify_attached is True:
            source_file = self.file_service._queue(downloaded_path, artifact, FileService.FILE_PREFIX_NONE)
        else:
            source_file = downloaded_path
        with self.os_service.open_file(source_file, mode=mode) as f:
            f_stream = f
        return f_stream

    @property
    def file_handles(self):
        return sorted(list(set([call[0] for call in self.call_stack])))

    @property
    def file_handle_name_tuples(self):
        return [(call[0], call[1][0]) for call in self.call_stack]


class MockedStreamCatcher(StringIO.StringIO):
    """
    Acts as StringIO stream object, but also catches all calls to write
    to be used in tests
    """
    def __init__(self):
        StringIO.StringIO.__init__(self)
        self.write_calls = list()

    def write(self, s):
        StringIO.StringIO.write(self, s)
        self.write_calls.append(s)


class FakeOsService:
    def __init__(self):
        self.filesystem = fake_filesystem.FakeFilesystem()
        self.os_module = FakeOsModule(self.filesystem)
        self.fake_shutils_module = FakeShutilModule(self.filesystem)
        self.write_calls = dict()

    def listdir(self, path):
        return self.os_module.listdir(path)

    def makedirs(self, path):
        print('Creating directory: {}'.format(path))
        self.os_module.makedirs(path)

    def _add_call(self, path, text):
        file_name = os.path.basename(path)
        if not self.write_calls.has_key(file_name):
            self.write_calls[file_name] = list()
        self.write_calls[file_name].append(text)

    @contextmanager
    def open_file(self, path, mode):
        file_module = FakeFileOpen(self.filesystem)

        mybuffer = StringIO.StringIO()
        if self.exists(path):
            with file_module(path) as file_object:
                c = "".join([line for line in file_object])
            mybuffer.write(c)

        def read(n=-1):
            mybuffer.seek(0)
            return mybuffer.read(n)

        def write(text):
            self._add_call(path, text)
            mybuffer.seek(os.SEEK_END)
            mybuffer.write(text)
            if self.exists(path):
                with file_module(path) as file_object:
                    cts = ''.join([line for line in file_object])
                text = '{}{}'.format(cts, text)
                self.remove_file(path)
            self.filesystem.CreateFile(path, contents=text)

        file_module.read = read
        file_module.write = write
        yield file_module

    def copy_file(self, src, dst):
        with self.open_file(src, 'r') as f:
            c = f.read()
        if self.exists(dst):
            self.remove_file(dst)
        self.filesystem.CreateFile(dst, contents=c)
        #self.fake_shutils_module.copyfile(src, dst)

    def exists(self, path):
        return self.os_module.path.exists(path)

    def remove_file(self, path):
        self.os_module.unlink(path)

    def create_file(self, file_path, contents=''):
        self.filesystem.CreateFile(file_path, contents=contents)


class FakeLogger:
    def __init__(self):
        self.info_messages = list()
        self.debug_messages = list()
        self.log_messages = list()

    def info(self, text):
        self.info_messages.append(text)

    def debug(self, text):
        self.debug_messages.append(text)

    def log(self, text):
        print('from fake logger log: {}'.format(text))
        self.log_messages.append(text)