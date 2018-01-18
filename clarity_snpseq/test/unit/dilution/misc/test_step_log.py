import unittest
import datetime
from unittest import skip
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_ext.service.step_logger_service import AggregatedStepLoggerService
from clarity_ext.service.step_logger_service import StepLoggerService
from clarity_ext.domain.validation import UsageError


class TestStepLog(TestDilutionBase):
    def save_step_log_to_harddisk(self, step_log_contents, extension, save_directory):
        file_service = self._file_service(extension, save_directory)
        # Modified code taken from DilutionSession.execute()
        today = datetime.date.today().strftime("%y%m%d")
        step_log_file_handle = "Step log"
        step_log_files = list()
        print("Saving files to harddisk in folder {}".format(save_directory))
        file_name = "step_log_{}.txt".format(today)
        step_log_files.append((file_name, step_log_contents))
        print("file: {}".format(file_name))

        # Upload the metadata file:
        file_service.upload_files(step_log_file_handle, step_log_files)
        self.assertEqual("", "Saving to harddisk makes it fail!")

    def test__with_dilution_has_usage_error__two_write_calls_to_step_log(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension(mock_file_service=True)
        # ordinary sample, pipette volume too high
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=350,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        try:
            builder.extension.execute()
        except UsageError:
            pass
        # self.save_step_log_to_harddisk(builder.step_log_contents, builder.extension,
        #                                r'C:\Smajobb\2018\Januari\clarity\saves')

        # Assert
        self.assertEqual(2, len(builder.step_log_calls))

    def test__with_normal_dilution__two_write_calls_to_step_log(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension(mock_file_service=True)
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(2, len(builder.step_log_calls))

    def test__with_dilution_has_usage_error__usage_error_written_to_step_log(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension(mock_file_service=True)
        # ordinary sample, pipette volume too high
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=350,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        try:
            builder.extension.execute()
        except UsageError:
            pass

        # Assert
        self.assertTrue('Error' in builder.step_log_contents)
