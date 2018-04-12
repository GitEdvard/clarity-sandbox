from StringIO import StringIO
from clarity_ext.service.file_service import Csv


class LocalSharedFilePatcher:
    """
    Replace methods in Context
    """
    def __init__(self):
        self.cache = dict()

    def local_shared_file(self, name, mode="r", is_xml=False, is_csv=False, file_name_contains=None):
        if is_csv:
            content = self.cache[name]
            stream = StringIO(content)
            return Csv(stream)
        else:
            raise NotImplementedError


class UseQcFlagPatcher:
    def use_qc_flag_from_current_state(self, artifact):
        pass
