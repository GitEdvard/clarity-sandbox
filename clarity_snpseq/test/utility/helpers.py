from __future__ import print_function
import functools
import os
from clarity_ext.domain import *
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository
from clarity_snpseq.test.utility.fake_artifacts import DilutionAnalyteCreator
from clarity_snpseq.test.utility.fake_collaborators import FakeOsService
from clarity_snpseq.test.utility.fake_collaborators import MonkeyMethodsForFileService
from clarity_snpseq.test.utility.fake_collaborators import FakeLogger
from clarity_ext.domain.validation import ValidationException
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class DilutionHelpers:
    def create_helper(self, extension=None, source_type=Analyte, target_type=Analyte):

        dil_helper = DilutionAnalyteCreator(extension.get_dilution_settings().concentration_ref)
        dil_helper.create_dilution_pair = functools.partial(dil_helper.create_dilution_pair,
                                                            source_type=source_type,
                                                            target_type=target_type)
        return dil_helper


class FileServiceInitializer:
    def __init__(self, extension):
        self.extension = extension
        self.os_service = FakeOsService()
        self.mocked_file_service = MonkeyMethodsForFileService(extension.context.file_service, self.os_service)

    def run(self):
        print('run file service initializer')
        CONTEXT_FILES_ROOT = self.extension.context.file_service.CONTEXT_FILES_ROOT
        self.upload_queue_path = os.path.join(CONTEXT_FILES_ROOT, "upload_queue")
        self.uploaded_path = os.path.join(CONTEXT_FILES_ROOT, "uploaded")
        self.temp_path = os.path.join(CONTEXT_FILES_ROOT, "temp")
        self.downloaded_path = os.path.join(CONTEXT_FILES_ROOT, "downloaded")

        self.os_service.makedirs(self.upload_queue_path)
        self.os_service.makedirs(self.uploaded_path)
        self.os_service.makedirs(self.temp_path)
        self.os_service.makedirs(self.downloaded_path)

        self._monkey_patch_local_shared_file()
        self._inject_fake_os_service_to_file_service()
        self._mock_logger()

    def _monkey_patch_local_shared_file(self):
        self.extension.context.file_service.local_shared_file_search_or_create = \
            self.mocked_file_service.mock_search_or_create
        self.extension.context.file_service.local_shared_file = \
            self.mocked_file_service.mock_search_existing

    def _inject_fake_os_service_to_file_service(self):
        self.extension.context.file_service.os_service = self.os_service

    def _mock_logger(self):
        self.extension.context.file_service.logger = FakeLogger()


class StepLogService:
    def __init__(self, context, os_service):
        self.os_service = os_service
        self.context = context

    @property
    def step_log_contents(self):
        # Step log is in test replaced with a StringIO
        # In production it's a file like object reading from hard disk
        step_log = self.context.validation_service.\
            step_logger_service.default_step_logger_service.step_log
        return step_log.read()

    @property
    def step_log_calls(self):
        print('write_calls')
        keys = [key for key in self.os_service.write_calls]
        print(keys)
        return self.os_service.write_calls['Step_log.txt']

    def write_to_step_log_explicitly(self, text):
        e = ValidationException(text)
        print('write to step log')
        self.context.validation_service.handle_single_validation(e)

    @property
    def _artifact(self):
        return utils.single([f for _, f in self.context.step_repo._shared_files if f.name == 'Step log'])

    def set_specific_lims_id(self, id):
        """
        id is without the prefix 92-
        :param id:
        :return:
        """
        artifact = self._artifact
        artifact.id = '92-{}'.format(id)

    @staticmethod
    def create():
        builder = ContextBuilder()
        builder.with_shared_result_file('Step log')
        os_service = builder.os_service
        return StepLogService(context=builder.context,
                              os_service=os_service)


class SimpleStepLogService:
    def __init__(self):
        self.messages = list()
        self.file_handle = ''

    def log(self, msg):
        self.messages.append(msg)

    def warning(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


class OsUtility:
    def __init__(self, os_service):
        self.os_service = os_service

    def get_contents(self, path):
        with self.os_service.open_file(path, 'r') as f:
            c = f.read()
        return c
