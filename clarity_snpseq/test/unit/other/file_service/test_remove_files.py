import unittest
from unittest import skip
from clarity_snpseq.test.utility.misc_builders import ContextWrapperBuilder
from clarity_snpseq.test.utility.helpers import OsUtility


class TestRemoveFiles(unittest.TestCase):
    def setUp(self):
        self.builder = ContextWrapperBuilder()
        self.os_utility = OsUtility(self.builder.context_wrapper.os_service)
        self.os_service = self.builder.context_wrapper.os_service

    def test_remove_step_log_from_artifact__with_step_log_added_in_advance__unlinking_happens(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876,
                                             existing_file_name='warnings.txt',
                                             existing_contents='x')
        self.builder.with_mocked_logger()
        file_service = self.builder.context_wrapper.context.file_service

        # Act
        file_service.remove_files('Step log', disabled=True)

        # Assert
        messages = self.builder.context_wrapper.context.file_service.logger.info_messages
        removed_files = [m for m in messages if 'Removing (disabled) file:' in m]
        removed_warning_files = [m for m in removed_files if 'warnings' in m.lower()]
        self.assertEqual(1, len(removed_warning_files))

    def test_remove_file_from_artifact__with_file_added_in_advance__field_for_files_updated(self):
        # Arrange
        artifact = self.builder.with_shared_result_file('Step log', with_id=9876,
                                                        existing_file_name='warnings.txt',
                                                        existing_contents='x')
        file_service = self.builder.context_wrapper.context.file_service

        # Act
        file_service.remove_files('Step log', disabled=True)

        # Assert
        self.assertEqual(0, len(artifact.files))

    def test_remove_file_from_artifact__with_two_files_added_and_one_excluded__excluded_file_remains(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876,
                                                        existing_file_name='warnings.txt',
                                                        existing_contents='x')
        excluded_artifact = self.builder.with_shared_result_file('Step log', with_id=9877,
                                                        existing_file_name='Step_log.log',
                                                        existing_contents='x')
        file_service = self.builder.context_wrapper.context.file_service
        exclude_list = ['Step_log.log']

        # Act
        file_service.remove_files('Step log', disabled=True, exclude_list=exclude_list)

        # Assert
        self.assertEqual(1, len(excluded_artifact.files))
        self.assertEqual('Step_log.log', excluded_artifact.files[0].original_location)

    def test_remove_file_from_artifact__with_two_files_added_and_one_excluded__intended_file_removed(self):
        # Arrange
        unlinked_artifact = self.builder.with_shared_result_file('Step log', with_id=9876,
                                                        existing_file_name='warnings.txt',
                                                        existing_contents='x')
        excluded_artifact = self.builder.with_shared_result_file('Step log', with_id=9877,
                                                        existing_file_name='Step_log.log',
                                                        existing_contents='x')
        file_service = self.builder.context_wrapper.context.file_service
        exclude_list = ['Step_log.log']

        # Act
        file_service.remove_files('Step log', disabled=True, exclude_list=exclude_list)

        # Assert
        self.assertEqual(0, len(unlinked_artifact.files))
