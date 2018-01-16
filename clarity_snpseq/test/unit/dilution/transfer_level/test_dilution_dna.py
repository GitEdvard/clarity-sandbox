import unittest
from unittest import skip
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestDilutionDNA(TestDilutionBase):
    def test__with_no_split_rows_no_looped__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(1, len(transfers))
        self.assertEqual(33.8, transfers[0].pipette_sample_volume)
        self.assertEqual(1.2, transfers[0].pipette_buffer_volume)

    def test__with_target_volume_less_than_2__1_warning(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=20, target_vol=1,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()

        # Assert
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        messages = list(builder.extension.dilution_session.validation_service.messages)
        self.assertEqual(0, error_count)
        self.assertEqual(1, len(messages))
        self.assertEqual(1, warning_count)

    @skip
    def test__with_target_volume_less_than_2__warning_for_scale_up(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=20, target_vol=1,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()

        # Assert
        messages = list(builder.extension.dilution_session.validation_service.messages)
        print(messages[0])
        self.assertEqual(1, 1)

    def test__with_looped_not_enough__1_warning(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=5,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        self.assertEqual(0, error_count)
        self.assertEqual(1, warning_count)

    def test__with_looped_not_enough__warning_message_has_scaled_up(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=5,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()

        # Assert
        messages = list(builder.extension.dilution_session.validation_service.messages)
        self.assertTrue('scaled up' in messages[0])
