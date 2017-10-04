from __future__ import print_function
import unittest
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestControls(TestDilutionBase):
    def test__with_two_ordinary_and_one_control__control_sorted_as_ordinary_sample(self):
        # Control samples are always placed in DNA1, so they should sort before the second ordinary sample
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="source2")

        # Act
        builder.extension.execute()


        # Assert
        transfers = builder.sorted_transfers
        self.assertTrue("in-FROM:A:1" == transfers[0].source_location.artifact.name or
                        "Negative control" == transfers[0].source_location.artifact.name)
        self.assertTrue("in-FROM:A:1" == transfers[1].source_location.artifact.name or
                        "Negative control" == transfers[1].source_location.artifact.name)
        self.assertEqual("in-FROM:B:1", transfers[2].source_location.artifact.name)
