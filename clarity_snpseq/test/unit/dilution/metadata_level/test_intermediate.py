from __future__ import print_function
import unittest
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestIntermediateDilution(TestDilutionBase):
    def test__with_one_multistep_sample__two_batches(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "default"]))
        self.assertEqual(1, len([b for b in batches if b.name == "looped"]))

    def test__with_one_multistep_sample__original_source_plate_source_in_looped(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(1,len(looped_batch.target_container_slots))
        self.assertEqual("DNA1", looped_batch.source_container_slots[0].name)
        self.assertEqual("source1", looped_batch.source_container_slots[0].container.name)

    def test__with_one_multistep_sample__temp_plate_as_target_in_looped(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(1,len(looped_batch.target_container_slots))
        self.assertEqual("END1", looped_batch.target_container_slots[0].name)
        self.assertEqual("Temp", looped_batch.target_container_slots[0].container.name)

    def test__with_one_multistep_sample__two_driver_files(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        files = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name).driver_files
        self.assertEqual(2, len(files))
        self.assertEqual(1, len([key for key in files if str(key) == "looped"]))
        self.assertEqual(1, len([key for key in files if str(key) == "default"]))

    def test__with_one_multistep_sample__temp_plate_as_source_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp", default_batch.source_container_slots[0].container.name)

    def test__with_one_multistep_sample__original_target_is_target_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("END1", default_batch.target_container_slots[0].name)
        self.assertEqual("target1", default_batch.target_container_slots[0].container.name)

    def test__with_one_multistep_one_ordinary__two_source_plates_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)

        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source1", default_batch.source_container_slots[1].container.name)

    def test__with_mixed_samples_in_one_source_plate__two_source_plates_in_final(self):
        # Arrange
        # context_builder = ContextBuilder()
        # context_builder.with_all_files()
        # builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder=context_builder)
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary samples
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)
        # builder.extension.execute()

        # Assert
        # self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source1", default_batch.source_container_slots[1].container.name)

    def test__with_two_multistep_in_separate_plates__one_target_plate_in_looped(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(1, len(looped_batch.target_container_slots))

    def test__with_three_source_plates_number_2_is_looped__slot_positioning_in_final_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source3", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(3, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source1", default_batch.source_container_slots[1].container.name)
        self.assertEqual("DNA3", default_batch.source_container_slots[2].name)
        self.assertEqual("source3", default_batch.source_container_slots[2].container.name)

    def test__with_three_source_plates_number_1_and_3_is_looped__source_slots_in_looped_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source3", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(2, len(looped_batch.source_container_slots))
        self.assertEqual("DNA1", looped_batch.source_container_slots[0].name)
        self.assertEqual("source1", looped_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", looped_batch.source_container_slots[1].name)
        self.assertEqual("source3", looped_batch.source_container_slots[1].container.name)

    def test__with_three_source_plates_number_1_and_3_is_looped__source_slots_in_final_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source3", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source2", default_batch.source_container_slots[1].container.name)
