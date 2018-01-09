from __future__ import print_function
import functools
import logging
import StringIO
from clarity_ext.domain import *
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.fixed_dilution_start import Extension as ExtensionFixed
from clarity_ext.utility.testing import TestExtensionWrapper
from clarity_ext.utility.testing import DilutionTestDataHelper
from clarity_ext.service.validation_service import ValidationService


class DilutionHelpers:
    def create_helpers(self, ext_type=ExtensionDna, source_type=Analyte, target_type=Analyte, logging_level=logging.CRITICAL):
        """
        Copied from test_dilution...
         Returns a tuple of valid (TestExtensionWrapper, DilutionTestHelper)
         """
        ext_wrapper = TestExtensionWrapper(ext_type)

        mocked_file_service = MockedUploadService(ext_wrapper.extension.context.file_service)
        self.monkey_patch_local_shared_file(ext_wrapper.extension, mocked_file_service)

        context_wrapper = ext_wrapper.context_wrapper
        context_wrapper.add_shared_result_file(SharedResultFile(name="Step log"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Evaporate step 1"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Evaporate step 1"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Evaporate step 2"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Evaporate step 2"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Intermediate"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Intermediate"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Metadata"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Metadata"))
        #context_wrapper.context.file_service.upload_queue_path = r'C:\Smajobb\2017\Oktober\tmp'
        context_wrapper.context.disable_commits = True

        # Re-define handle single validation, it has been mocked out previously in clarity-ext!
        validation_service = ValidationService(context_wrapper.context.validation_service.step_logger_service)
        context_wrapper.context.validation_service.handle_single_validation = \
            validation_service.handle_single_validation
        context_wrapper.context.validation_service.messages = validation_service.messages

        if ext_type == ExtensionFixed:
            context_wrapper.add_udf_to_step("Volume in destination ul", 10)

        dil_helper = DilutionTestDataHelper(ext_wrapper.extension.get_dilution_settings().concentration_ref)
        dil_helper.create_dilution_pair = functools.partial(dil_helper.create_dilution_pair,
                                                            source_type=source_type,
                                                            target_type=target_type)
        DilutionHelpers._handle_loggers(ext_wrapper, context_wrapper, logging_level)
        return ext_wrapper, dil_helper, mocked_file_service


    def monkey_patch_local_shared_file(self, extension, mocked_file_service):
        extension.context.file_service.local_shared_file = \
            mocked_file_service.mock_local_shared_file

    @staticmethod
    def _handle_loggers(extension_wrapper, context_wrapper, logging_level):
        extension_wrapper.extension.logger.setLevel(logging_level)
        context_wrapper.context.dilution_service.logger.setLevel(logging_level)
        context_wrapper.context.file_service.logger.setLevel(logging_level)


class MockedUploadService:
    def __init__(self, file_service):
        self.call_stack = []
        self.file_service = file_service
        self.local_shared_file_buffer = MockedStreamCatcher()

    def mock_upload_files(self, file_handle, files_with_name):
        self.call_stack.append((file_handle, files_with_name))

    def mock_upload_single(self, artifact, file_handle, instance_name, content, file_prefix):
        self.file_service.artifactid_by_filename[instance_name] = artifact.id
        files_with_name = [(instance_name, content)]
        self.call_stack.append((file_handle, files_with_name))

    def mock_local_shared_file(self, file_handle, mode='r', extension="", modify_attached=False, file_name_contains=None):
        return self.local_shared_file_buffer

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