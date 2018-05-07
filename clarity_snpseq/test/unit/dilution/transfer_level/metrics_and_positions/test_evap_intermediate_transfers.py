import unittest
from clarity_ext import utils
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory


class TestEvapIntermediateTransfer(TestDilutionBase):
    def test__with_one_evap_one_looped_one_ordinary__entries_in_files_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        self.assertEqual(4, len(batches))
        self.assertEqual(1, len(evap1_batch.transfers))
        self.assertEqual(1, len(evap2_batch.transfers))
        self.assertEqual(1, len(loop_batch.transfers))
        self.assertEqual(2, len(default_batch.transfers))

    def test__with_one_evap_one_looped_one_ordinary__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_evap_step1 = utils.single(evap1_batch.transfers)
        transfer_evap_step2 = utils.single(evap2_batch.transfers)
        transfer_loop = utils.single(loop_batch.transfers)
        default_transfers = sorted(default_batch.transfers, key=self.sort_strategy.input_position_sort_key)
        self.assertEqual(15, transfer_evap_step1.pipette_sample_volume)
        self.assertEqual(0, transfer_evap_step1.pipette_buffer_volume)
        self.assertEqual(0, transfer_evap_step2.pipette_sample_volume)
        self.assertEqual(10, transfer_evap_step2.pipette_buffer_volume)
        self.assertEqual(4, transfer_loop.pipette_sample_volume)
        self.assertEqual(36, transfer_loop.pipette_buffer_volume)
        self.assertEqual(2, default_transfers[0].pipette_sample_volume)
        self.assertEqual(8, default_transfers[0].pipette_buffer_volume)
        self.assertEqual(3, default_transfers[1].pipette_sample_volume)
        self.assertEqual(7, default_transfers[1].pipette_buffer_volume)
