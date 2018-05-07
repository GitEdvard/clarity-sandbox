import unittest
from clarity_ext import utils
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestIntermediateTransfers(TestDilutionBase):
    def test__with_one_looped__number_entries_in_files_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len(loop_batch.transfers))
        self.assertEqual(1, len(default_batch.transfers))

    def test__with_one_looped__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_loop = utils.single(loop_batch.transfers)
        transfer_default = utils.single(default_batch.transfers)
        self.assertEqual(4, transfer_loop.pipette_sample_volume)
        self.assertEqual(36, transfer_loop.pipette_buffer_volume)
        self.assertEqual(2, transfer_default.pipette_sample_volume)
        self.assertEqual(8, transfer_default.pipette_buffer_volume)

    def test__with_one_looped__looped_hamilton_driver_file_ok(self):
        # Arrange
        # context_builder = ContextBuilder()
        # context_builder.with_all_files()
        # builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder)
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)
        # builder.extension.execute()

        # Assert
        # self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')
        content = builder.loop_batch.driver_file.to_string(include_header=False)
        self.assertEqual('in-FROM:A:1\t1\tDNA1\t4.0\t36.0\t1\tEND1\tsource1\t1111111111\t0', content)

    def test__with_one_looped__final_hamilton_driver_file_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        content = builder.default_batch.driver_file.to_string(include_header=False)
        self.copy_to_clipboard(content)
        self.assertEqual('in-FROM:A:1-looped\t1\tDNA1\t2.0\t8.0\t1\tEND1\t1111111111\ttarget1\t0', content)

    def test__with_one_looped_one_ordinary__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_loop = utils.single(loop_batch.transfers)
        sorted_transfers = sorted(default_batch.transfers, key=self.sort_strategy.input_position_sort_key)
        self.assertEqual(4, transfer_loop.pipette_sample_volume)
        self.assertEqual(36, transfer_loop.pipette_buffer_volume)
        self.assertEqual(2, sorted_transfers[0].pipette_sample_volume)
        self.assertEqual(8, sorted_transfers[0].pipette_buffer_volume)
        self.assertEqual(3, sorted_transfers[1].pipette_sample_volume)
        self.assertEqual(7, sorted_transfers[1].pipette_buffer_volume)

    def test__with_two_looped_one_ordinary__number_entries_in_files_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        self.assertEqual(2, len(batches))
        self.assertEqual(2, len(loop_batch.transfers))
        self.assertEqual(3, len(default_batch.transfers))
