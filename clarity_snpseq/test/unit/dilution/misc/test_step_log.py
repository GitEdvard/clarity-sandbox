import datetime
from unittest import skip
from clarity_ext.domain.validation import UsageError
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.utility.misc_builders import ContextInitializor
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestStepLog(TestDilutionBase):
    def setUp(self):
        initializor = ContextInitializor()
        self.logger = initializor.with_fake_logger()
        builder = ContextBuilder(initializor)
        builder.with_shared_result_file(file_handle="Step log", with_id=9877, existing_file_name='Warnings.txt')
        builder.with_shared_result_file(file_handle="Step log", with_id=9878, existing_file_name='Errors.txt')
        self.ext_builder = ExtensionBuilder.create_with_dna_extension(context_builder=builder)
        self.ext_builder.with_evaluate_and_log_only()


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
        self.ext_builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=350,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        try:
            self.ext_builder.extension.execute()
        except UsageError:
            pass
        # self.save_step_log_to_harddisk(builder.step_log_contents, builder.extension,
        #                                r'C:\Smajobb\2018\Januari\clarity\saves')

        # Assert
        self.assertEqual(2, len(self.ext_builder.extension.context.logger.log_messages))

    def test__with_normal_dilution__two_write_calls_to_step_log(self):
        # Arrange

        # Ordinary sample
        self.ext_builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.ext_builder.extension.execute()

        # Assert
        self.assertEqual(2, len(self.ext_builder.extension.context.logger.log_messages))

    def test__with_dilution_has_usage_error__usage_error_written_to_step_log(self):
        # Arrange
        # ordinary sample, pipette volume too high
        self.ext_builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=350,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        try:
            self.ext_builder.extension.execute()
        except UsageError:
            pass

        # Assert
        self.assertTrue('Error' in self.logger.log_messages[-1])
