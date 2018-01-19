from clarity_snpseq.test.utility.testing import TestExtensionContext
from clarity_ext.domain.shared_result_file import SharedResultFile
from clarity_ext.utils import single


class ContextWrapperBuilder:
    def __init__(self):
        self.context_wrapper = TestExtensionContext()

    def with_shared_result_file(self, file_handle, with_id=None):
        self.context_wrapper.add_shared_result_file(SharedResultFile(name=file_handle))
        if with_id is not None:
            self._update_artifact_id(file_handle, with_id)

    def _update_artifact_id(self, file_handle, new_id):
        file_service = self.context_wrapper.context.file_service
        artifact = self._artifact(file_service)
        artifact.id = '92-{}'.format(9876)

    def _artifact(self, file_service):
        return single([f for f in file_service.artifact_service.shared_files() if f.name == 'Step log'])
