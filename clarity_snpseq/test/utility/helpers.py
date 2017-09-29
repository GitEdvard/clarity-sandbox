from __future__ import print_function
import functools
import logging
from clarity_ext.domain import *
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.fixed_dilution_start import Extension as ExtensionFixed
from clarity_ext.utility.testing import TestExtensionWrapper
from clarity_ext.utility.testing import DilutionTestDataHelper


class DilutionHelpers:

    @staticmethod
    def create_helpers(ext_type=ExtensionDna, source_type=Analyte, target_type=Analyte, logging_level=logging.CRITICAL):
        """
        Copied from test_dilution...
         Returns a tuple of valid (TestExtensionWrapper, DilutionTestHelper)
         """
        ext_wrapper = TestExtensionWrapper(ext_type)

        context_wrapper = ext_wrapper.context_wrapper
        context_wrapper.add_shared_result_file(SharedResultFile(name="Step log"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Final"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Metadata"))
        context_wrapper.add_shared_result_file(SharedResultFile(name="Metadata"))

        if ext_type == ExtensionFixed:
            context_wrapper.add_udf_to_step("Volume in destination ul", 10)

        dil_helper = DilutionTestDataHelper(ext_wrapper.extension.get_dilution_settings().concentration_ref)
        dil_helper.create_dilution_pair = functools.partial(dil_helper.create_dilution_pair,
                                                            source_type=source_type,
                                                            target_type=target_type)
        DilutionHelpers._handle_loggers(ext_wrapper, context_wrapper, logging_level)
        return ext_wrapper, dil_helper

    @staticmethod
    def _handle_loggers(extension_wrapper, context_wrapper, logging_level):
        extension_wrapper.extension.logger.setLevel(logging_level)
        context_wrapper.context.dilution_service.logger.setLevel(logging_level)
        context_wrapper.context.upload_file_service.logger.setLevel(logging_level)
