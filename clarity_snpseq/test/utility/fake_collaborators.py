from __future__ import print_function
import StringIO
import os
from mock import MagicMock
from pyfakefs import fake_filesystem
from pyfakefs.fake_filesystem import FakeOsModule
from pyfakefs.fake_filesystem_shutil import FakeShutilModule
from pyfakefs.fake_filesystem import FakeFileOpen
from contextlib import contextmanager
from clarity_ext.service.file_service import FileService
from clarity_ext.domain.process import Process
from clarity_ext.domain.user import User
from clarity_ext.domain.process import ProcessType


class FakeFileService:
    def __init__(self):
        artifact_service = MagicMock()
        artifact_service.shared_files = self._shared_files_method
        os_service = FakeOsService()
        file_repository = FakeFileRepository(os_service)
        self.file_service = FileService(artifact_service=artifact_service,
                                        file_repo=file_repository, should_cache=False,
                                        os_service=os_service)

        self._shared_files = list()
        self._analytes = list()

    def _all_artifacts(self):
        return self._shared_files + self._analytes

    def _shared_files_method(self):
        return self._shared_files


class FakeFileRepository:
    def __init__(self, os_service):
        self.os_service = os_service
        self.file_by_id = dict()

    def copy_remote_file(self, remote_file_id, local_path):
        self.os_service.create_file(local_path, self.file_by_id[remote_file_id].contents)

    def open_local_file(self, local_path, mode):
        with self.os_service.open_file(local_path, 'r') as f:
            contents = f.read()
            f_out = f
        return f_out

    def add_file(self, id, filename, contents):
        file = FakeFile(id=id, contents=contents, filename=filename)
        self.file_by_id[id] = file


class FakeFile:
    """
    Represent a genologics File object
    """
    def __init__(self, id, contents, filename=None):
        self.id = id
        self.contents = contents
        self.original_location = filename
        self.api_resource = None
        self.uri = r'www.something/{}'.format(filename)


class FakeApiResource:
    def __init__(self):
        self.files = list()


class MonkeyMethodsForFileService:
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

    def mock_search_existing(self, file_handle, mode='r', extension="", modify_attached=False,
                               file_name_contains=None):
        artifact = self.file_service.local_shared_file_provider._artifact_by_name(file_handle, file_name_contains)
        self._local_shared_file(file_handle, artifact, mode=mode, extension=extension,
                                modify_attached=modify_attached)

    def mock_search_or_create(self, file_handle, mode='r', extension="", modify_attached=False,
                               filename=None):
        provider = self.file_service.local_shared_file_provider
        artifact = provider._artifact_by_name(file_handle,
                                              filename,
                                              fallback_on_first_unassigned=True)
        self._local_shared_file(file_handle, artifact, mode=mode, extension=extension,
                                modify_attached=modify_attached)

    def _local_shared_file(self, file_handle, artifact, mode='r', extension="", modify_attached=False):
        local_file_name = "{}_{}.{}".format(artifact.id, file_handle.replace(" ", "_"), extension)
        downloaded_path = os.path.join(self.file_service.downloaded_path, local_file_name)
        if not self.os_service.exists(downloaded_path):
            self.os_service.create_file(downloaded_path)
        if modify_attached is True:
            source_file = self.file_service.queue(downloaded_path, artifact, FileService.FILE_PREFIX_NONE)
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

    def makedirs(self, path, printout=False):
        if self.exists(path):
            return
        if printout:
            print('Creating directory: {}'.format(path))
        self.os_module.makedirs(path)

    def mkdir(self, path):
        self.makedirs(path)

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

    def copy(self, src, dst):
        src_base = os.path.basename(src)
        dst_base = os.path.basename(dst)
        if src_base != dst_base:
            basename = os.path.basename(src)
            dst = os.path.join(dst, basename)
        self.copy_file(src, dst)

    def exists(self, path):
        return self.os_module.path.exists(path)

    def remove_file(self, path):
        self.os_module.unlink(path)

    def create_file(self, file_path, contents=''):
        self.filesystem.CreateFile(file_path, contents=contents)

    def abspath(self, path):
        return path


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

    def error(self, text):
        self.log_messages.append(text)


class FakeStepRepo:
    def __init__(self):
        self._shared_files = list()
        self._analytes = list()
        self.user = User("Integration", "Tester", "no-reply@medsci.uu.se", "IT")

    def all_artifacts(self):
        return self._shared_files + self._analytes

    def add_shared_result_file(self, f):
        assert f.name is not None, "You need to supply a name"
        f.id = "92-{}".format(len(self._shared_files))
        self._shared_files.append((None, f))

    def add_analyte_pair(self, input, output):
        self._analytes.append((input, output))

    def get_process(self):
        return Process(None, "24-1234", self.user, None, "http://not-avail")

    def current_user(self):
        return self.user

    def get_process_type(self):
        return ProcessType(None, None, name="Some process")
