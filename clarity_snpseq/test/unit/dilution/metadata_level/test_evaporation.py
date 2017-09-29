from __future__ import print_function
import unittest
from clarity_ext.domain import *
from clarity_ext_scripts.dilution.settings import HamiltonRobotSettings
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestEvaporation(TestDilutionBase):
    @unittest.skip("")
    def test__with_one_evaporate_one_ordinary__investigate_variables(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        metadata_info = builder.metadata_info("Metadata filename", HamiltonRobotSettings())
        print_list(metadata_info.container_mappings, "container mappings")
        self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')

    def test__with_one_evaporate_sample__two_transfer_batches(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "default"]))
        self.assertEqual(1, len([b for b in batches if b.name == "evaporate"]))

    def test__with_one_evaporate_sample__one_source_container_slot_in_final(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(1,len(default_batch.source_container_slots))

    def test__with_one_evaporate_one_ordinary__two_driver_files(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        robot_setting = HamiltonRobotSettings()
        files = builder.extension.dilution_session.transfer_batches(robot_setting.name).driver_files
        print_list(files, "files")
        self.assertEqual(2, len(files))
        self.assertEqual(1, len([key for key in files if str(key) == "default"]))
        self.assertEqual(1, len([key for key in files if str(key) == "evaporate"]))

    def test__with_one_evaporate_one_ordinary__two_batches(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        for batch in batches:
            print("batch name: {}".format(batch.name))
            print_list(batch.container_mappings, "container mapping")
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "default"]))
        self.assertEqual(1, len([b for b in batches if b.name == "evaporate"]))

    #@unittest.skip("Fails, part of lims-1427")
    def test__with_one_evaporate_one_ordinary__one_source_container_slot_in_final(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(1,len(default_batch.source_container_slots))
        self.assertEqual(1,len(default_batch.target_container_slots))

    def test__with_three_source_plates_second_is_evaporation__final_slot_positioning_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source2", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source3", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        print_list(default_batch.source_container_slots, "final slot positioning")
        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("source1", default_batch.source_container_slots[0].container.name)
        self.assertEqual("source3", default_batch.source_container_slots[1].container.name)
