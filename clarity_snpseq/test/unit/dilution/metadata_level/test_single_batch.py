
import unittest
import re
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_ext.domain.validation import UsageError


class TestSingleBatch(TestDilutionBase):
    def test__with_two_source_plates__end_plate_only_appears_once(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source2", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Oktober\clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        self.print_list(batches[0].container_mappings, "container mapping")
        self.assertEqual(1, len(batches))
        self.assertEqual(2, len(batches[0].source_container_slots))
        self.assertEqual(1, len(batches[0].target_container_slots))

    def test__with_one_single_sample__driver_file_name_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        files = batches.driver_files
        file_names = [files[key].file_name for key in files]
        regexp = re.match("hamilton_", file_names[0])
        self.assertEqual(1, len(batches))
        self.assertEqual(1, len(file_names))
        self.assertTrue(regexp is not None)
        self.assertEqual("hamilton_", regexp.group(0))

    def test__with_one_single_sample_pipette_volume_too_high__exception_cast(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        # ordinary sample, pipette volume too high
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=350,
                                  source_container_name="source1", target_container_name="target1")

        self.assertRaises(UsageError, builder.extension.execute)

    def test__with_three_source_plates__slot_sort_order_correct(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary samples
        builder.add_artifact_pair(source_container_name="8source1", target_container_name="target1")
        builder.add_artifact_pair(source_container_name="9source1", target_container_name="target1")
        builder.add_artifact_pair(source_container_name="10source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        default_batch = builder.default_batch
        self.assertEqual(3, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("8source1", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("9source1", default_batch.source_container_slots[1].container.name)
        self.assertEqual("DNA3", default_batch.source_container_slots[2].name)
        self.assertEqual("10source1", default_batch.source_container_slots[2].container.name)
