from __future__ import print_function
import unittest
from clarity_ext.domain import *
from clarity_ext_scripts.dilution.settings.file_rendering import HamiltonRobotSettings
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestEvaporation(TestDilutionBase):
    @unittest.skip("")
    def test__with_one_evaporate_one_ordinary__investigate_variables(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        metadata_info = builder.metadata_info("Metadata filename", HamiltonRobotSettings())
        self.print_list(metadata_info.container_mappings, "container mappings")
        self.save_metadata_to_harddisk(builder, r'C:\Smajobb\2017\Augusti\Clarity\saves')

    def test__with_one_evaporate_sample__two_transfer_batches(self):
        # Arrange
        # context_builder = ContextBuilder()
        # context_builder.with_all_files()
        # builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder=context_builder)
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)
        #builder.extension.execute()

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')
        #self.save_robot_files_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "evaporate1"]))
        self.assertEqual(1, len([b for b in batches if b.name == "evaporate2"]))

    def test__with_one_evaporate_sample__one_source_container_slot_in_evaporate_step2(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "evaporate2")
        evap2_batch = next(gen)
        self.assertEqual(1,len(evap2_batch.source_container_slots))

    def test__with_one_evaporate_sample__source_slot_in_evaporate_step2_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "evaporate2")
        evap2_batch = next(gen)

        self.print_list([t.source_location.container.name for t in evap2_batch.transfers], "source locations")

        self.assertEqual(1,len(evap2_batch.source_container_slots))
        self.assertEqual("DNA1", evap2_batch.source_container_slots[0].name)
        self.assertEqual("source1", evap2_batch.source_container_slots[0].container.name)

    def test__with_one_evaporate_sample__two_driver_files(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        files = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name).driver_files
        self.print_list(files, "files")
        self.assertEqual(2, len(files))
        self.assertEqual(1, len([key for key in files if str(key) == "evaporate1"]))
        self.assertEqual(1, len([key for key in files if str(key) == "evaporate2"]))

    def test__with_two_evaporate_samples__one_source_container_slot_in_evaporate_step_2(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "evaporate2")
        default_batch = next(gen)
        self.assertEqual(1,len(default_batch.source_container_slots))

    def test__with_one_evaporate_one_ordinary__three_driver_files(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        robot_setting = HamiltonRobotSettings()
        files = builder.extension.dilution_session.transfer_batches(robot_setting.name).driver_files
        #self.save_metadata_to_harddisk(builder.extension, r"C:\Smajobb\2017\Oktober\clarity\saves")
        self.print_list(files, "files")
        self.assertEqual(3, len(files))
        self.assertEqual(1, len([key for key in files if str(key) == "evaporate1"]))
        self.assertEqual(1, len([key for key in files if str(key) == "evaporate2"]))
        self.assertEqual(1, len([key for key in files if str(key) == "default"]))

    def test__with_one_evaporate_one_ordinary__one_sample_in_evap_slot(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        evap_batch = builder.evap2_batch
        target_slot = utils.single(evap_batch.target_container_slots)
        target_container = target_slot.container
        self.assertEqual(1, len(target_container.occupied))

    def test__with_one_evaporate_one_ordinary__correct_sample_names_in_evap_dest_plate(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        evap_batch = builder.evap2_batch
        target_slot = utils.single(evap_batch.target_container_slots)
        target_container = target_slot.container
        self.assertEqual("out-FROM:B:1", target_container.occupied[0].artifact.name)

    def test__with_one_evaporate_one_ordinary__two_samples_in_final_slot(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Oktober\clarity\saves')

        target_slot = utils.single(builder.default_batch.target_container_slots)
        target_container = target_slot.container
        self.assertEqual(2, len(target_container.occupied))


    @unittest.skip("")
    def test_test(self):
        def fnk(pos, *args):
            print("pos argument: {}".format(pos))
            return sum(args)
        res = fnk("hej", 1, 2, 4)
        self.assertEqual(0, res)

    @unittest.skip("Not implemented yet")
    def test__with_one_evaporate_one_ordinary__check_driver_file_names(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        robot_setting = HamiltonRobotSettings()
        files = builder.extension.dilution_session.transfer_batches(robot_setting.name).driver_files
        #self.save_metadata_to_harddisk(builder.extension, r"C:\Smajobb\2017\Oktober\clarity\saves")
        file_names = [files[key].file_name for key in files]
        self.print_list(sorted(file_names), "files")
        self.assertEqual(3, len(files))
        self.assertEqual(1, len([name for name in file_names if "step1-hamilton-evaporate1" in name]))
        self.assertEqual(1, len([name for name in file_names if "step2-hamilton-evaporate2" in name]))
        self.assertEqual(1, len([name for name in file_names if "step3-hamilton_" in name]))

    def test__with_one_evaporate_one_ordinary__three_batches(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r"C:\Smajobb\2017\Oktober\clarity\saves")
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        for batch in batches:
            print("batch name: {}".format(batch.name))
            self.print_list(batch.container_mappings, "container mapping")
        self.assertEqual(3, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "default"]))
        self.assertEqual(1, len([b for b in batches if b.name == "evaporate1"]))
        self.assertEqual(1, len([b for b in batches if b.name == "evaporate2"]))

    def test__with_one_evaporate_one_ordinary__one_source_container_slot_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(1,len(default_batch.source_container_slots))
        self.assertEqual(1,len(default_batch.target_container_slots))

    def test__with_one_evaporate_one_control__source_slot_in_final_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()

        # control
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="control container",
                                  target_container_name="target1", is_control=True)

        # evaporation
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Oktober\clarity\saves')
        default_batch = builder.default_batch
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("control container", default_batch.source_container_slots[0].container.name)

    def test__with_three_source_plates_second_is_evaporation__final_slot_positioning_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # Name and id on containers are the same in test. Set ids for containers
        # so that they are sorted in a specific way
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="1source1", target_container_name="2target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source2", target_container_name="2target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="3source3", target_container_name="2target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.print_list(default_batch.source_container_slots, "final slot positioning")
        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("1source1", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("3source3", default_batch.source_container_slots[1].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
