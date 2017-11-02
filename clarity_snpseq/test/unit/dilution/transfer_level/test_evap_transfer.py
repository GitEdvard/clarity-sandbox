import unittest
from clarity_ext import utils
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_ext_scripts.dilution.settings import TRANSFER_COMMAND_NEW_TIPS
from clarity_ext_scripts.dilution.settings import TRANSFER_COMMAND_NONE


class TestEvapTransfer(TestDilutionBase):
    def test__with_one_evap_sample__number_entries_in_files_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len(evap1_batch.transfers))
        self.assertEqual(1, len(evap2_batch.transfers))

    def test__with_one_evap_sample__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        transfer_step1 = utils.single(evap1_batch.transfers)
        transfer_step2 = utils.single(evap2_batch.transfers)
        self.assertEqual(15, transfer_step1.pipette_sample_volume)
        self.assertEqual(0, transfer_step1.pipette_buffer_volume)
        self.assertEqual(0, transfer_step2.pipette_sample_volume)
        self.assertEqual(10, transfer_step2.pipette_buffer_volume)

    def test__with_one_evap_sample__custom_command_in_evaporate1_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        transfer_step1 = utils.single(evap1_batch.transfers)
        self.assertEqual(TRANSFER_COMMAND_NONE, transfer_step1.custom_command)

    def test__with_one_evap_sample__custom_command_in_evaporate2_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        transfer_step2 = utils.single(evap2_batch.transfers)
        self.assertEqual(TRANSFER_COMMAND_NEW_TIPS, transfer_step2.custom_command)

    def test__with_one_evap_one_ordinary__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_step1 = utils.single(evap1_batch.transfers)
        transfer_step2 = utils.single(evap2_batch.transfers)
        transfer_default = utils.single(default_batch.transfers)
        self.assertEqual(15, transfer_step1.pipette_sample_volume)
        self.assertEqual(0, transfer_step1.pipette_buffer_volume)
        self.assertEqual(0, transfer_step2.pipette_sample_volume)
        self.assertEqual(10, transfer_step2.pipette_buffer_volume)
        self.assertEqual(3, transfer_default.pipette_sample_volume)
        self.assertEqual(7, transfer_default.pipette_buffer_volume)

    def test__with_one_evap_one_control__hamilton_control_row_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # control
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="control container",
                                  target_container_name="target1", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        default_batch = self.default_batch(builder)
        row = self.hamilton_robot_setting.map_transfer_to_row(default_batch.transfers[0])
        self.assertEqual(1, len(default_batch.transfers))
        self.assertEqual("Negative control", default_batch.transfers[0].source_location.artifact.name)
        self.assertEqual("Negative control, 1, DNA1, 0.0, 35.0, 2, END1, source1, target1, 0",
                         ", ".join(map(str, row)))

    def test__with_two_evap_one_ordinary__number_entries_in_files_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        self.assertEqual(3, len(batches))
        self.assertEqual(2, len(evap1_batch.transfers))
        self.assertEqual(2, len(evap2_batch.transfers))
        self.assertEqual(1, len(default_batch.transfers))

    def test__with_one_evap_one_ordinary__custom_command_in_default_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        default_batch = utils.single([b for b in batches if b.name == "default"])
        default_transfer = utils.single(default_batch.transfers)
        self.assertEqual(TRANSFER_COMMAND_NONE, default_transfer.custom_command)

    def test__with_one_evap_one_ordinary__custom_command_in_evaporation2_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        evap2_transfer = utils.single(evap2_batch.transfers)
        self.assertEqual(TRANSFER_COMMAND_NEW_TIPS, evap2_transfer.custom_command)
