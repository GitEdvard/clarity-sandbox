from contextlib import contextmanager
from StringIO import StringIO
from io import BytesIO
from mock import MagicMock
from clarity_ext.service.file_service import Csv
from clarity_ext.service.file_service import FileService
from clarity_snpseq.test.utility.fake_collaborators import FakeOsService


class LocalSharedFilePatcher:
    """
    Replace methods in Context
    """
    def __init__(self):
        self.cache = dict()
        self.file_service = FileService(None, None, False, FakeOsService())

    def local_shared_file(self, name, mode="r", is_xml=False, is_csv=False, file_name_contains=None):
        @contextmanager
        def fake_stream(io_obj):
            yield io_obj

        if is_csv:
            content = self.cache[name]
            stream = StringIO(content)
            return Csv(stream)
        else:
            content = self.cache[name]
            bs = BytesIO(b'{}'.format(content.encode('utf-8')))
            return self.file_service.parse_xml(bs)


class ResultFilePatcher:
    def __init__(self):
        self.cache = dict()

    def output_result_file_by_id(self, file_id):
        return self.cache[file_id]


class UseQcFlagPatcher:
    def use_qc_flag_from_current_state(self, artifact):
        pass
