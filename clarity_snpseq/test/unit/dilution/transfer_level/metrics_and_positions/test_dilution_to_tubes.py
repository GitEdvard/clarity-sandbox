import unittest
from unittest import skip
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestDilutionToTubes(TestDilutionBase):
    def test_volumes(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(1, len(transfers))
        self.assertEqual(5.0, transfers[0].pipette_sample_volume)
        self.assertEqual(5.0, transfers[0].pipette_buffer_volume)

    skip("wip")
    def test_positions(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(2, len(transfers))
        self.assertEqual("in-FROM:B:1", transfers[1].source_location.artifact.name)
        self.assertEqual(2, transfers[1].source_location.index_down_first)
        self.assertEqual("DNA1", transfers[1].source_slot.name)
        self.assertEqual("out-FROM:B:1", transfers[1].target_location.artifact.name)
        self.assertEqual(2, transfers[1].target_location.index_down_first)
        self.assertEqual("END1", transfers[1].target_slot.name)

    def test_initialization_with_tubes(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(2, len(transfers))
        self.assertEqual("in-FROM:B:1", transfers[1].source_location.artifact.name)
        self.assertEqual(2, transfers[1].source_location.index_down_first)
        self.assertEqual("DNA1", transfers[1].source_slot.name)
        self.assertEqual("out-FROM:B:1", transfers[1].target_location.artifact.name)
        self.assertEqual(1, transfers[1].target_location.index_down_first)
        self.assertEqual("END1", transfers[1].target_slot.name)
