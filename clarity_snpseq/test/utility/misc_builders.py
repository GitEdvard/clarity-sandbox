import os
from mock import MagicMock
from clarity_snpseq.test.utility.testing import TestExtensionContext
from clarity_ext.domain.shared_result_file import SharedResultFile
from clarity_ext.utils import single
from clarity_snpseq.test.utility.fake_collaborators import FakeApiResource
from clarity_snpseq.test.utility.fake_collaborators import FakeLogger


class ContextBuilder:
    def __init__(self):
        self.context_wrapper = TestExtensionContext()
        self.file_repository = self.context_wrapper.context.file_service.file_repo
        self.file_service = self.context_wrapper.context.file_service
        self.id_counter = 0
        self.my_mock = MagicMock()

    def with_shared_result_file(self, file_handle, with_id=None, existing_file_name=None,
                                existing_contents=None):
        artifact = SharedResultFile(name=file_handle, api_resource=self.my_mock)
        self.context_wrapper.add_shared_result_file(artifact)
        if with_id is not None:
            artifact.id = '92-{}'.format(with_id)
        if existing_file_name is not None or existing_contents is not None:
            self._add_existing_file(artifact, existing_file_name, existing_contents)
        return artifact

    def with_cached_file(self, filename, contents):
        cached_path = os.path.join(r'.cache\{}'.format(filename))
        self.context_wrapper.os_service.create_file(cached_path, contents)

    def with_should_cache(self, should_cache):
        """Update file service and local shared file provider"""
        self.context_wrapper.context.file_service.should_cache = should_cache
        self.context_wrapper.context.file_service.local_shared_file_provider.should_cache = should_cache

    def _add_existing_file(self, artifact, existing_file_name, existing_contents):
        self.file_repository.add_file(self.id_counter, existing_file_name, existing_contents)
        existing_file = self.file_repository.file_by_id[self.id_counter]
        artifact.files.append(existing_file)
        api_resource = FakeApiResource()
        api_resource.files.append(existing_file)
        artifact.api_resource = api_resource
        self.id_counter += 1

    def _artifact(self, file_service, file_handle):
        return single([f for f in file_service.artifact_service.shared_files() if f.name == file_handle])

    def with_mocked_logger(self):
        logger = FakeLogger()
        self.file_service.logger = logger
