import os
from mock import MagicMock
from clarity_ext.domain.shared_result_file import SharedResultFile
from clarity_ext.service.artifact_service import ArtifactService
from clarity_ext.service.file_service import FileService
from clarity_ext.service.step_logger_service import StepLoggerService
from clarity_ext.service.validation_service import ValidationService
from clarity_ext.service.dilution.service import DilutionService
from clarity_ext.service.process_service import ProcessService
from clarity_ext.context import ExtensionContext
from clarity_ext.utils import single
from clarity_snpseq.test.utility.fake_collaborators import FakeApiResource
from clarity_snpseq.test.utility.fake_collaborators import FakeLogger
from clarity_snpseq.test.utility.fake_collaborators import FakeFileRepository
from clarity_snpseq.test.utility.fake_collaborators import FakeOsService
from clarity_snpseq.test.utility.fake_collaborators import FakeStepRepo
from clarity_ext.domain.udf import UdfMapping


class ContextBuilder:
    """
    Add entities to repositories held by context
    E.g. shared files, artifacts, analytes.
    """
    def __init__(self, context_initiator=None):
        self.os_service = FakeOsService()
        if context_initiator is None:
            context_initiator = ContextInitializor()
        context_initiator.with_os_service(self.os_service)
        context_initiator.create()
        self.context_initiator = context_initiator
        self.context = context_initiator.context
        self.file_repository = context_initiator.context.file_service.file_repo
        self.file_service = context_initiator.context.file_service
        self.step_repo = self.context_initiator.step_repo
        self.id_counter = 0

    def with_all_files(self):
        self.with_shared_result_file(file_handle="Step log")
        self.with_shared_result_file(file_handle="Step log")
        self.with_shared_result_file(file_handle="Step log")
        self.with_shared_result_file(file_handle="Final")
        self.with_shared_result_file(file_handle="Final")
        self.with_shared_result_file(file_handle="Evaporate step 1")
        self.with_shared_result_file(file_handle="Evaporate step 1")
        self.with_shared_result_file(file_handle="Evaporate step 2")
        self.with_shared_result_file(file_handle="Evaporate step 2")
        self.with_shared_result_file(file_handle="Intermediate")
        self.with_shared_result_file(file_handle="Intermediate")
        self.with_shared_result_file(file_handle="Metadata")
        self.with_shared_result_file(file_handle="Metadata")
        self.context_wrapper.context.disable_commits = True

    def with_shared_result_file(self, file_handle, with_id=None, existing_file_name=None,
                                existing_contents=None):
        artifact = SharedResultFile(name=file_handle)
        self.step_repo.add_shared_result_file(artifact)
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

    def add_analyte_pair(self, input, output):
        self.step_repo.add_analyte_pair(input, output)

    def add_shared_result_file(self, f):
        self.step_repo.add_shared_result_file(f)

    def with_mocked_logger(self):
        logger = FakeLogger()
        self.file_service.logger = logger


class ContextInitializor:
    """
    Initiate repositories of context to either fake instances or real instances.
    Create context with the configured repositories at the time chosen by the client.
    """
    def __init__(self):
        self.session = MagicMock()
        self.clarity_service = MagicMock()
        self.step_repo = None
        self.os_service = None
        self.step_logger_service = None
        self.validation_service = None
        self.file_repository = None
        self.artifact_service = None
        self.current_user = None
        self.file_service = None
        self.context = None

    def with_os_service(self, os_service):
        self.os_service = os_service

    def with_fake_logger(self):
        logger = FakeLogger()
        self.step_logger_service = logger
        return logger

    def _init_with_default(self):
        """
        with_os_service() and with_get_all_artifacts() must have been called prior of this call!
        :return:
        """
        self.step_repo = FakeStepRepo()
        self.file_repository = FakeFileRepository(self.os_service)
        self.artifact_service = ArtifactService(self.step_repo)
        self.current_user = self.step_repo.current_user()
        self.file_service = FileService(self.artifact_service, self.file_repository, False, self.os_service,
                                   uploaded_to_stdout=False,
                                   disable_commits=True)
        if self.step_logger_service is None:
            self.step_logger_service = StepLoggerService("Step log", self.file_service)
        self.validation_service = ValidationService(self.step_logger_service)
        self.dilution_service = DilutionService(self.validation_service)
        self.process_service = ProcessService()

    def create(self):
        self._init_with_default()
        self.context = ExtensionContext(self.session, self.artifact_service, self.file_service, self.current_user,
                                self.step_logger_service, self.step_repo, self.clarity_service,
                                self.dilution_service, self.process_service, self.validation_service,
                                test_mode=False, disable_commits=True)
