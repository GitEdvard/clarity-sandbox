from clarity_snpseq.test.utility.testing import TestExtensionContext
from clarity_ext.domain.shared_result_file import SharedResultFile


class ContextWrapperBuilder:
    def __init__(self):
        self.context_wrapper = TestExtensionContext()

    def with_shared_result_file(self, file_handle):
        self.context_wrapper.add_shared_result_file(SharedResultFile(name=file_handle))