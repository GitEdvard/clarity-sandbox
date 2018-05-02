from __future__ import print_function
import unittest
import re
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_ext.domain.validation import UsageError
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestFixedDilution(TestDilutionBase):

    def test__with_one_sample__one_transfer_batch(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_fixed_extension()
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1')

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(1, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "default"]))

    def test__with_one_sample__source_container_slot_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_fixed_extension()
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1')

        # Act
        self.execute_short(builder)

        # Assert
        self.assertEqual(1, len(builder.default_batch.source_container_slots))
        self.assertEqual('DNA1', builder.default_batch.source_container_slots[0].name)
        self.assertEqual('source1', builder.default_batch.source_container_slots[0].container.name)

    def test__with_two_samples_from_different_plates__two_source_slots(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_fixed_extension()
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1')
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source2',
                                  target_container_name='target1')

        # Act
        self.execute_short(builder)

        # Assert
        self.assertEqual(2, len(builder.default_batch.source_container_slots))

    def test__with_two_samples_from_different_plates__source_container_slot1_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_fixed_extension()
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1')
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source2',
                                  target_container_name='target1')

        # Act
        self.execute_short(builder)

        # Assert
        self.assertEqual(2, len(builder.default_batch.source_container_slots))
        self.assertEqual('DNA1', builder.default_batch.source_container_slots[0].name)
        self.assertEqual('source1', builder.default_batch.source_container_slots[0].container.name)

    def test__with_two_samples_from_different_plates__source_container_slot2_ok(self):
        # Arrange
        # b = ContextBuilder()
        # b.with_all_files()
        # builder = ExtensionBuilderFactory.create_with_fixed_extension(b)
        builder = ExtensionBuilderFactory.create_with_fixed_extension()
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source1',
                                  target_container_name='target1')
        builder.add_artifact_pair(source_vol=40, target_vol=5, source_container_name='source2',
                                  target_container_name='target1')

        # Act
        self.execute_short(builder)
        # builder.extension.execute()

        # Assert
        # self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Maj\clarity\saves')
        self.assertEqual(2, len(builder.default_batch.source_container_slots))
        self.assertEqual('DNA2', builder.default_batch.source_container_slots[1].name)
        self.assertEqual('source2', builder.default_batch.source_container_slots[1].container.name)
