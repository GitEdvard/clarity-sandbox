import unittest
from unittest import skip
from clarity_ext.domain.validation import UsageError
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestDilutionDNA(TestDilutionBase):
    def test__with_target_volume_less_than_2__1_warning(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=20, target_vol=1,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        messages = list(builder.extension.dilution_session.validation_service.messages)
        self.assertEqual(0, error_count)
        self.assertEqual(1, len(messages))
        self.assertEqual(1, warning_count)

    @skip('Wait to implement this case')
    def test__with_target_volume_less_than_2__warning_for_scale_up(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=20, target_vol=1,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        messages = list(builder.extension.dilution_session.validation_service.messages)
        print(messages[0])
        self.assertEqual(1, 1)

    def test__with_looped_not_enough__1_warning(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=5,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        self.assertEqual(0, error_count)
        self.assertEqual(1, warning_count)

    def test__with_looped_not_enough__warning_message_has_scaled_up(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=5,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        messages = list(builder.extension.dilution_session.validation_service.messages)
        #self.copy_to_clipboard(messages)
        self.assertTrue('scaled up' in messages[0])

    def test__with_sample_volume_too_small_at_single_batch__1_warning(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=10, source_vol=4, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        self.assertEqual(0, error_count)
        self.assertEqual(1, warning_count)

    def test__with_sample_volume_too_small_at_looped__1_warning(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=100, source_vol=2, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        self.assertEqual(0, error_count)
        self.assertEqual(1, warning_count)

    def test__with_input_lacking_conc__exception(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=None, source_vol=2, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.execute_short(builder))

    def test__with_input_lacking_vol__exception(self):
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=100, source_vol=None, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.execute_short(builder))

    def test__with_target_lacking_conc__exception(self):
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=100, source_vol=2, target_conc=None, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.execute_short(builder))

    def test__with_target_lacking_vol__exception(self):
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=100, source_vol=2, target_conc=2, target_vol=None,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.execute_short(builder))

    @skip
    def test__with_input_lacking_conc__printout(self):
        # Arrange
        b = ContextBuilder()
        b.with_all_files()
        builder = ExtensionBuilder.create_with_dna_extension(b)
        builder.add_artifact_pair(source_conc=100, source_vol=2, target_conc=2, target_vol=200,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        try:
            self.execute_short(builder)
        except UsageError:
            self.copy_to_clipboard(b.context.validation_service.messages)

        # Assert
        self.assertEqual(1, 2)

    def test__with_total_pipette_volume_too_high__exception(self):
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=100, source_vol=2, target_conc=2, target_vol=200,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.execute_short(builder))
