import unittest
from unittest import skip
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestDilutionDNA(TestDilutionBase):
    def test__with_no_split_rows_no_looped__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(1, len(transfers))
        self.assertAlmostEqual(33.8, transfers[0].pipette_sample_volume, places=1)
        self.assertAlmostEqual(1.2, transfers[0].pipette_buffer_volume, places=1)
