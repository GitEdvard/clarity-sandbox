import unittest
from unittest import skip
from clarity_snpseq.test.utility.helpers import ContextBuilder
from clarity_snpseq.test.utility.helpers import OsUtility
from clarity_ext.service.file_service import SharedFileNotFound


class TestStepLog(unittest.TestCase):
    def setUp(self):
        self.builder = ContextBuilder()
        self.os_utility = OsUtility(self.builder.context_wrapper.os_service)
        self.os_service = self.builder.context_wrapper.os_service

    def test_search_existing__with_one_artifact_unassigned__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file('Step log', mode='ab', extension='txt',
                                                       modify_attached=True)

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Step_log.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_existing__with_one_artifact_already_assign__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876, existing_contents='existing')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file('Step log', mode='ab', extension='txt',
                                                       modify_attached=True)

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Step_log.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_existing__with_one_artifact_already_assigned__file_contents_OK(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876, existing_contents='existing')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        # Assert
        f = file_service.local_shared_file('Step log', mode='r', extension='txt',
                                                                  modify_attached=True)
        contents = f.read()
        self.assertEqual('existing', contents)

    def test_search_existing__with_search_by_name_from_two_artifact_already_assigned__file_found(self):
        # Note! Not intuitive file name in downloaded
        # Arrange
        self.builder.with_shared_result_file('FileHandleX', with_id=9876, existing_file_name='file1',
                                        existing_contents='existing1')
        self.builder.with_shared_result_file('FileHandleX', with_id=9877, existing_file_name='file2',
                                        existing_contents='existing2')
        file_service = self.builder.context_wrapper.context.file_service

        # Act
        file_service.local_shared_file('FileHandleX', mode='r', extension='txt',
                                                       file_name_contains='file2',
                                                       modify_attached=False)

        # Assert
        queue_path = r'./context_files\downloaded\92-9877_FileHandleX.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_existing__with_two_assigned_artifacts_without_search__exception(self):
        # Arrange
        self.builder.with_shared_result_file('FileHandleX', with_id=9876, existing_file_name='file1',
                                        existing_contents='existing1')
        self.builder.with_shared_result_file('FileHandleX', with_id=9877, existing_file_name='file2',
                                        existing_contents='existing2')
        file_service = self.builder.context_wrapper.context.file_service

        # Act
        # Assert
        with self.assertRaises(SharedFileNotFound):
            file_service.local_shared_file(
                'FileHandleX', mode='r', extension='txt', modify_attached=False)

    def test_search_existing__with_two_unassigned_artifacts_without_search__exception(self):
        # Arrange
        self.builder.with_shared_result_file('FileHandleX', with_id=9876)
        self.builder.with_shared_result_file('FileHandleX', with_id=9877)
        file_service = self.builder.context_wrapper.context.file_service

        # Act
        # Assert
        with self.assertRaises(SharedFileNotFound):
            file_service.local_shared_file(
                'FileHandleX', mode='r', extension='txt', modify_attached=False)

    def test_search_or_create__with_one_artifact_unassigned__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Warnings.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_or_create__with_one_artifact_assigned_and_matching__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876, existing_file_name='Warnings',
                                        existing_contents='x')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Warnings.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_or_create_then_write__with_one_artifact_assigned_and_matching__file_contents_ok(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876, existing_file_name='Warnings',
                                        existing_contents='x')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file = file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)
        file.write('new contents')
        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Warnings.txt'
        contents = self.os_utility.get_contents(queue_path)
        self.assertEqual('xnew contents', contents)

    def test_search_or_create__with_one_artifact_assigned_to_other__exception(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876,
                                        existing_file_name='another_file',
                                        existing_contents='x')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        # Assert
        with self.assertRaises(SharedFileNotFound):
            file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                          extension='txt', modify_attached=True)

    def test_search_or_create__two_calls_with_diff_files_and_only_one_artifact__exception(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)
        # Assert
        with self.assertRaises(SharedFileNotFound):
            file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Errors',
                                          extension='txt', modify_attached=True)

    def test_search_or_create__with_two_artifacts_unassigned__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        self.builder.with_shared_result_file('Step log', with_id=9877)
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Warnings.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_or_create__with_match_from_two_assigned_artifacts__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876, existing_file_name='Step_log')
        self.builder.with_shared_result_file('Step log', with_id=9877, existing_file_name='Warnings',
                                        existing_contents='previous text')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)

        # Assert
        queue_path = r'./context_files\upload_queue\92-9877\Warnings.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_or_create__with_match_from_one_assigned_and_one_unassigned__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        self.builder.with_shared_result_file('Step log', with_id=9877, existing_file_name='Warnings',
                                        existing_contents='previous text')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)

        # Assert
        queue_path = r'./context_files\upload_queue\92-9877\Warnings.txt'
        self.assertTrue(self.os_service.exists(queue_path))

    def test_search_or_create_then_write__with_match_from_one_assingned_and_one_unassigned__file_contents_ok(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        self.builder.with_shared_result_file('Step log', with_id=9877, existing_file_name='Warnings',
                                        existing_contents='previous text ')
        file_service = self.builder.context_wrapper.context.file_service
        # Act
        f = file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)
        f.write('new contents')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9877\Warnings.txt'
        contents = self.os_utility.get_contents(queue_path)
        self.assertEqual('previous text new contents', contents)

    def test_search_existing__with_cache_on_and_cache_path_exists__cache_file_copied_to_current_dir(self):
        # Arrange
        file_service = self.builder.context_wrapper.context.file_service
        self.builder.with_shared_result_file('FileHandleX', with_id=9876)
        self.builder.with_should_cache(True)
        self.builder.with_cached_file('92-9876_FileHandleX.txt', contents='cached contents')
        # Act
        file_service.local_shared_file('FileHandleX', mode='r', extension='txt',
                                                       modify_attached=False)

        # Assert
        copied_path = r'./92-9876_FileHandleX.txt'
        self.assertTrue(self.os_service.exists(copied_path))
        self.assertEqual('cached contents', self.os_utility.get_contents(copied_path))

    def test_search_existing__with_cache_on_and_cache_path_non_existing__file_copied_to_cache(self):
        # Arrange
        file_service = self.builder.context_wrapper.context.file_service
        self.builder.with_shared_result_file('FileHandleX', with_id=9876, existing_file_name='FileHandleX',
                                             existing_contents='downloaded contents')
        self.builder.with_should_cache(True)
        # Act
        file_service.local_shared_file('FileHandleX', mode='r', extension='txt',
                                                       modify_attached=False)

        # Assert
        copied_path = r'./.cache\92-9876_FileHandleX.txt'
        self.assertTrue(self.os_service.exists(copied_path))
        self.assertEqual('downloaded contents', self.os_utility.get_contents(copied_path))

    def test_write_to_search_or_create__with_existing_file_removed__only_new_contents(self):
        # Note, it is never created a local file in production or test until it's already removed.
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876, existing_file_name='Warnings',
                                        existing_contents='previous text ')
        file_service = self.builder.context_wrapper.context.file_service
        file_service.remove_files('Step log', disabled=True)
        # Act
        f = file_service.local_shared_file_search_or_create('Step log', mode='ab', filename='Warnings',
                                      extension='txt', modify_attached=True)
        f.write('new contents')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Warnings.txt'
        contents = self.os_utility.get_contents(queue_path)
        self.assertEqual('new contents', contents)
