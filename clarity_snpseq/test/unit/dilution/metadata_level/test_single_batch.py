from __future__ import print_function
import unittest
import re
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestSingleBatch(TestDilutionBase):
    def test__with_two_source_plates__end_plate_only_appears_once(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source2", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        print_list(batches[0].container_mappings, "container mapping")
        self.assertEqual(1, len(batches))
        self.assertEqual(2, len(batches[0].source_container_slots))
        self.assertEqual(1, len(batches[0].target_container_slots))

    def test__with_one_single_sample__driver_file_name_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

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
