import unittest
import datetime
from unittest import skip
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
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
        builder = ExtensionBuilder.create_with_dna_extension()
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
        builder = ExtensionBuilder.create_with_dna_extension()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(2, len(builder.step_log_calls))

    def test__with_dilution_has_usage_error__usage_error_written_to_step_log(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
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

    def test__with_text_to_step_log_explicitly__step_log_saved_in_upload_queue(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        # execute() not needed!
        #builder.extension.execute()
        builder.step_log_service.set_specific_lims_id(9876)
        builder.write_to_step_log_explicitly('my message')

        # Assert
        queue_path = r'./context_files\upload_queue\92-9876\Step_log.log'
        #print(builder.extension.context.file_service.artifactid_by_filename)
        self.assertTrue(builder.mocked_file_service.os_service.exists(queue_path))

    def test_commit__with_normal_dilution__printouts_from_commit(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()
        builder.extension.context.file_service.commit(disable_commits=True)

        # Assert
        # Set to fail to see printouts
        self.assertEqual(1, 1)
