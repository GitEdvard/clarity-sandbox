from __future__ import print_function
import functools
import logging
import os
from mock import MagicMock
from clarity_ext.domain import *
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.fixed_dilution_start import Extension as ExtensionFixed
from clarity_snpseq.test.utility.testing import TestExtensionWrapper
from clarity_snpseq.test.utility.testing import DilutionTestDataHelper
from clarity_snpseq.test.utility.fake_collaborators import FakeOsService
from clarity_snpseq.test.utility.fake_collaborators import MonkeyMethodsForFileService
from clarity_snpseq.test.utility.fake_collaborators import FakeLogger
from clarity_ext.domain.validation import ValidationException
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class DilutionHelpers:
    def create_helpers(self, ext_type=ExtensionDna, source_type=Analyte, target_type=Analyte,
                       logging_level=logging.CRITICAL, context_builder=None):
        """
        Copied from test_dilution...
         Returns a tuple of valid (TestExtensionWrapper, DilutionTestHelper)
         """
        if context_builder is None:
            context_builder = self._init_default_context()
        ext_wrapper = TestExtensionWrapper(ext_type, context_builder)
        context_wrapper = ext_wrapper.context_wrapper

        if ext_type == ExtensionFixed:
            context_wrapper.add_udf_to_step("Volume in destination ul", 10)

        dil_helper = DilutionTestDataHelper(ext_wrapper.extension.get_dilution_settings().concentration_ref)
        dil_helper.create_dilution_pair = functools.partial(dil_helper.create_dilution_pair,
                                                            source_type=source_type,
                                                            target_type=target_type)
        DilutionHelpers._handle_loggers(ext_wrapper, context_wrapper, logging_level)
        return ext_wrapper, dil_helper

    def _init_default_context(self):
        builder = ContextBuilder()
        builder.with_all_files()
        return builder

    @staticmethod
    def _handle_loggers(extension_wrapper, context_wrapper, logging_level):
        extension_wrapper.extension.logger.setLevel(logging_level)
        context_wrapper.context.dilution_service.logger.setLevel(logging_level)
        context_wrapper.context.validation_service.logger.setLevel(logging_level)
        #context_wrapper.context.file_service.logger.setLevel(logging_level)


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
    def __init__(self, context_wrapper, os_service):
        self.os_service = os_service
        self.context_wrapper =context_wrapper

    @property
    def step_log_contents(self):
        # Step log is in test replaced with a StringIO
        # In production it's a file like object reading from hard disk
        step_log = self.context_wrapper.context.validation_service.\
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
        self.context_wrapper.context.validation_service.handle_single_validation(e)

    @property
    def _artifact(self):
        return utils.single([f for _, f in self.context_wrapper._shared_files if f.name == 'Step log'])

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
        os_service = builder.context_wrapper.context.file_service.os_service
        return StepLogService(context_wrapper=builder.context_wrapper,
                                             os_service=os_service)


class SimpleStepLogService:
    def __init__(self):
        self.messages = list()

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
