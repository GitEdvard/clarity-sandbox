import unittest
import sys
from importlib import import_module
sys.modules['lims_snpseq.labels'] = import_module('clarity_snpseq.test.utility.fake_labels')
from lims_snpseq.labels import label_printer
from clarity_ext_scripts.general.print_temp_container import Extension as PrintTempContainer
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository
from clarity_snpseq.test.utility.fake_labels import label_printer


class TestBarcodePrinter(unittest.TestCase):
    def test_first(self):
        # Arrange
        context_builder = ContextBuilder()
        builder = ExtensionBuilderFactory.create_with_base_type(
            PrintTempContainer, context_builder=context_builder)
        artifact_repo = FakeArtifactRepository()
        pair_builder = PairBuilderBase(artifact_repo)
        pair_builder.with_target_container_name('plate1')
        pair_builder.create()
        context_builder.with_analyte_pair(*pair_builder.pair)
        pair_builder = PairBuilderBase(artifact_repo)
        pair_builder.with_target_container_name('plate2')
        pair_builder.create()
        context_builder.with_analyte_pair(*pair_builder.pair)

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(2, len(label_printer.cache))
        self.assertEqual('Temp1', label_printer.cache[0].name)
        self.assertEqual('1111111111', label_printer.cache[0].barcode)
        self.assertEqual('Temp2', label_printer.cache[1].name)
        self.assertEqual('1111111112', label_printer.cache[1].barcode)
