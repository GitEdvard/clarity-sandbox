import unittest
from clarity_ext import utils
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder


class TestDriverFileAppearance(TestDilutionBase):
    def test__with_one_ordinary_sample__hamilton_driver_file_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        default_batch = utils.single([b for b in batches if b.name == "default"])
        contents = default_batch.driver_file.to_string(include_header=False)

        self.assertEqual("in-FROM:A:1\t1\tDNA1\t3.0\t7.0\t1\tEND1\tsource1\ttarget1\t0", contents)

    def test__with_one_evap_sample__hamilton_evaporate1_file_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        contents = evap1_batch.driver_file.to_string(include_header=False)

        self.assertEqual("in-FROM:A:1\t1\tDNA1\t15.0\t0.0\t1\tEND1\tsource1\ttarget1\t0", contents)

    def test__with_one_evap_sample__hamilton_evaporate2_file_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        contents = evap2_batch.driver_file.to_string(include_header=False)

        self.assertEqual("in-FROM:A:1\t1\tDNA1\t0.0\t10.0\t1\tEND1\tsource1\ttarget1\t1", contents)

    def test__with_one_evap_sample__biomek_evaporate1_file_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        contents = evap1_batch.driver_file.to_string(include_header=False)

        self.assertEqual("in-FROM:A:1,1,DNA1,15.0,0.0,1,END1,1,0", contents)

    def test__with_one_evap_sample_biomek_evaporate2_file_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        contents = evap2_batch.driver_file.to_string(include_header=False)

        self.assertEqual("in-FROM:A:1,1,DNA1,0.0,10.0,1,END1,1,1", contents)
