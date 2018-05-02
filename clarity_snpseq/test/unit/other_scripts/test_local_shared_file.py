import unittest
from unittest import skip
from clarity_ext.context import ExtensionContext
from clarity_ext.service.file_service import SharedFileNotFound
from clarity_snpseq.test.utility.higher_level_builders import ReadResultFileBuilder
from clarity_ext_scripts.qpcr.analyze_qpcr_resultfile import Extension as AnalyzeQpcrResultfile
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestLocalSharedFile(unittest.TestCase):
    """
    I want to test check file extension, because it's called by a bunch of scripts.
    """
    def test__with_shared_file_has_wrong_extension__exception(self):
        # Arrange
        builder = ContextBuilder()
        builder.with_shared_result_file('Result File (.csv) (required)',
                                             existing_file_name='something.xlsx')

        # Act
        # Assert
        self.assertRaises(SharedFileNotFound, lambda:
            builder.context.local_shared_file('Result File (.csv) (required)',
                                              is_csv=True))

    #@skip('cant get fake stream into local shared file')
    def test__with_shared_file_has_proper_extension__no_exception(self):
        #todo: get fake stream to work with local shared file
        # Arrange
        builder = ContextBuilder()
        builder.with_shared_result_file('Result File (.csv) (required)',
                                             existing_file_name='something.csv')

        # Act
        # Assert
        builder.context.local_shared_file('Result File (.csv) (required)',
                                          is_csv=True)

