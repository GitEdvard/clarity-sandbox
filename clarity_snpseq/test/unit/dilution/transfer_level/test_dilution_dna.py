import unittest
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestDilutionDNA(TestDilutionBase):
    def test__with_no_split_rows_no_looped__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(1, len(transfers))
        self.assertEqual(33.8, transfers[0].pipette_sample_volume)
        self.assertEqual(1.2, transfers[0].pipette_buffer_volume)
