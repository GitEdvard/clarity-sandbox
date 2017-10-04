from __future__ import print_function
import unittest
from clarity_ext.domain import *
from clarity_ext_scripts.dilution.settings import HamiltonRobotSettings
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestBothEvaporationAndIntermediate(TestDilutionBase):
    def test__with_one_evaporation_one_multistep_one_ordinary__four_batches(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # evaporation
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(4, len(batches))

    def test__with_one_evaporation_one_multistep_one_ordinary__two_source_plates_in_final(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # evaporation
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        #self.save_robot_files_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        print_list(default_batch.source_container_slots, "source slots")
        print_list(default_batch.container_mappings, "container mapping")
        self.assertEqual(2, len(default_batch.source_container_slots))
