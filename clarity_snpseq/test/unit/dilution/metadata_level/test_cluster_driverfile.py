
import unittest
import re
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_ext.domain.validation import UsageError
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestFixedDilution(TestDilutionBase):
    def test__with_one_sample__one_transfer_batch(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_cluster_driverfile_extension()
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1')

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(1, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "default"]))

    def test__with_two_samples_from_different_plates__two_source_container_slots(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_cluster_driverfile_extension()
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1')
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source2',
                                  target_container_name='target2')

        # Act
        self.execute_short(builder)
        # Assert

        #self.save_metadata_to_harddisk(builder, r'C:\Smajobb\2018\Maj\clarity\saves')
        self.assertEqual(2, len(builder.default_batch.source_container_slots))

    def test__with_two_control_samples_from_different_plates__only_one_source_container_slot(self):
        """
        This is a reflection of the current behaviour of the system.
        If this test fail, maybe the field is_control is made obsolete?
        """

        # Arrange
        builder = ExtensionBuilderFactory.create_with_cluster_driverfile_extension()
        builder.with_control_id_prefix('2-')
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1', is_control=True)
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source2',
                                  target_container_name='target2', is_control=True)

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder, r'C:\Smajobb\2018\Maj\clarity\saves')
        self.assertEqual(1, len(builder.default_batch.source_container_slots))
