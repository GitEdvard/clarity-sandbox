
import unittest
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestControls(TestDilutionBase):
    def test__with_two_ordinary_and_one_control__control_sorted_as_ordinary_sample(self):
        # Control samples are always placed in DNA1, so they should sort before the second ordinary sample
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="source2")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual("Negative control",transfers[0].source_location.artifact.name)
        self.assertEqual("in-FROM:source1-B:1", transfers[1].source_location.artifact.name)
        self.assertEqual("in-FROM:source2-C:1", transfers[2].source_location.artifact.name)

    def test__with_one_control_one_ordinary__source_positions_ok_in_driver_file(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(2, len(transfers))
        self.assertEqual("in-FROM:source1-A:1", transfers[0].source_location.artifact.name)
        self.assertEqual(1, transfers[0].source_location.index_down_first)
        self.assertEqual("DNA1", transfers[0].source_slot.name)
        self.assertEqual("Negative control", transfers[1].source_location.artifact.name)
        self.assertEqual(1, transfers[1].source_location.index_down_first)
        self.assertEqual("DNA1", transfers[1].source_slot.name)

    def test__with_one_control_one_ordinary__target_positions_ok_in_driver_file(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(2, len(transfers))
        self.assertEqual("out-FROM:source1-A:1", transfers[0].target_location.artifact.name)
        self.assertEqual(1, transfers[0].target_location.index_down_first)
        self.assertEqual("END1", transfers[0].target_slot.name)
        self.assertEqual("Negative control", transfers[1].target_location.artifact.name)
        self.assertEqual(2, transfers[1].target_location.index_down_first)
        self.assertEqual("END1", transfers[1].target_slot.name)
