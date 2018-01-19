import unittest
from unittest import skip
from clarity_ext.service.step_logger_service import AggregatedStepLoggerService
from clarity_ext.service.step_logger_service import StepLoggerService
from clarity_snpseq.test.utility.helpers import SimpleStepLogService
from clarity_snpseq.test.utility.helpers import StepLogService as MockedStepLogService
from clarity_snpseq.test.utility.helpers import ContextWrapperBuilder


class TestStepLog(unittest.TestCase):
    def test__with_text_to_step_log_explicitly__step_log_saved_in_upload_queue(self):
        # Arrange
        step_logger_service = MockedStepLogService.create()

        # Act
        step_logger_service.set_specific_lims_id(9876)
        step_logger_service.write_to_step_log_explicitly('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Step_log.log'
        self.assertTrue(step_logger_service.os_service.exists(queue_path))

    def test_write_to_step_log__with_one_message__step_log_saved_in_upload_queue(self):
        # Arrange
        builder = ContextWrapperBuilder()
        builder.with_shared_result_file('Step log', with_id=9876)
        file_service = builder.context_wrapper.context.file_service
        step_logger_service = StepLoggerService('Step log', file_service)
        # Act
        step_logger_service.log('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Step_log.log'
        self.assertTrue(builder.context_wrapper.os_service.exists(queue_path))

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
