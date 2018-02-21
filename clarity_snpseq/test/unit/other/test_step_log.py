import unittest
import re
from unittest import skip
from clarity_ext.service.step_logger_service import AggregatedStepLoggerService
from clarity_ext.service.step_logger_service import StepLoggerService
from clarity_snpseq.test.utility.helpers import SimpleStepLogService
from clarity_snpseq.test.utility.helpers import OsUtility
from clarity_snpseq.test.utility.helpers import StepLogService as MockedStepLogService
from clarity_snpseq.test.utility.helpers import ContextBuilder


class TestStepLog(unittest.TestCase):
    def setUp(self):
        self.builder = ContextBuilder()
        self.os_utility = OsUtility(self.builder.context_wrapper.os_service)
        self.os_service = self.builder.context_wrapper.os_service

    def test_write_to_step_log__with_one_message__step_log_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        file_service = self.builder.context_wrapper.context.file_service
        step_logger_service = StepLoggerService('Step log', file_service)
        # Act
        step_logger_service.log('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Step_log.txt'
        self.assertTrue(self.builder.context_wrapper.os_service.exists(queue_path))

    def test_write_to_step_log__with_one_message__contents_from_step_log_ok(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        file_service = self.builder.context_wrapper.context.file_service
        step_logger_service = StepLoggerService('Step log', file_service)
        # Act
        step_logger_service.log('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Step_log.txt'
        contents = self.os_utility.get_contents(queue_path)
        match = re.match('^\d+-\d+-\d+ \d+:\d+:\d+ - my message\r\n$', contents)
        self.assertTrue(match is not None)

    def test_write_to_step_log__with_filename_and_handle_different__file_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        file_service = self.builder.context_wrapper.context.file_service
        step_logger_service = StepLoggerService('Step log', file_service, extension='txt', filename='Warnings')
        # Act
        step_logger_service.warning('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Warnings.txt'
        self.assertTrue(self.builder.context_wrapper.os_service.exists(queue_path))

    def test_real_aggregated__with_one_warning__warning_step_log_saved_in_upload_queue(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        self.builder.with_shared_result_file('Step log', with_id=9877)
        file_service = self.builder.context_wrapper.context.file_service
        default_step_log = StepLoggerService('Step log', file_service, extension='txt')
        warning_step_log = StepLoggerService('Step log', file_service, extension='txt', filename='Warnings')
        aggregated_service = AggregatedStepLoggerService(default_step_log)
        aggregated_service.warnings_step_logger_service = warning_step_log
        # Act
        aggregated_service.warning('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9877\Warnings.txt'
        self.assertTrue(self.builder.context_wrapper.os_service.exists(queue_path))

    def test_real_aggregated__with_one_warning__warning_contents_ok(self):
        # Arrange
        self.builder.with_shared_result_file('Step log', with_id=9876)
        self.builder.with_shared_result_file('Step log', with_id=9877)
        file_service = self.builder.context_wrapper.context.file_service
        default_step_log = StepLoggerService('Step log', file_service, extension='txt')
        warning_step_log = StepLoggerService('Step log', file_service, extension='txt', filename='Warnings')
        aggregated_service = AggregatedStepLoggerService(default_step_log)
        aggregated_service.warnings_step_logger_service = warning_step_log
        # Act
        aggregated_service.warning('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9877\Warnings.txt'
        contents = self.os_utility.get_contents(queue_path)
        match = re.match('^WARNING - \d+-\d+-\d+ \d+:\d+:\d+ - my message\r\n$', contents)
        self.assertTrue(match is not None)

    def test_aggregated__with_log_call__1_message_in_standard_log(self):
        # Arrange
        default_service = SimpleStepLogService()
        warning_service = SimpleStepLogService()
        error_service = SimpleStepLogService()
        aggregated_service = AggregatedStepLoggerService(default_service,
                                                         warnings_step_logger_service=warning_service,
                                                         errors_step_logger_service=error_service)

        # Act
        aggregated_service.log('mymsg')

        # Assert
        self.assertEqual(1, len(default_service.messages))
        self.assertEqual(0, len(warning_service.messages))
        self.assertEqual(0, len(error_service.messages))

    def test_aggregated__with_warning_call__1_message_in_standard_log_and_warning_log(self):
        # Arrange
        default_service = SimpleStepLogService()
        warning_service = SimpleStepLogService()
        error_service = SimpleStepLogService()
        aggregated_service = AggregatedStepLoggerService(default_service,
                                                         warnings_step_logger_service=warning_service,
                                                         errors_step_logger_service=error_service)

        # Act
        aggregated_service.warning('mymsg')

        # Assert
        self.assertEqual(1, len(default_service.messages))
        self.assertEqual(1, len(warning_service.messages))
        self.assertEqual(0, len(error_service.messages))

    def test_aggregated__with_error_call__1_message_in_standard_log_and_error_log(self):
        # Arrange
        default_service = SimpleStepLogService()
        warning_service = SimpleStepLogService()
        error_service = SimpleStepLogService()
        aggregated_service = AggregatedStepLoggerService(default_service,
                                                         warnings_step_logger_service=warning_service,
                                                         errors_step_logger_service=error_service)

        # Act
        aggregated_service.error('mymsg')

        # Assert
        self.assertEqual(1, len(default_service.messages))
        self.assertEqual(0, len(warning_service.messages))
        self.assertEqual(1, len(error_service.messages))

