import unittest
from unittest import skip
from clarity_ext.domain.validation import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestDilutionFactor(TestDilutionBase):
    def test___with_single_transfer_looped_dilution___exception_cast(self):
        # Arrange
        builder = self.builder_with_factor_ext_and_all_files()
        builder.add_artifact_pair(source_vol=80, dilute_factor=35, target_vol=10)

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.execute_short(builder))

    def test___with_one_transfer_lacking_dilute_factor___exception_cast(self):
        # Arrange
        builder = self.builder_with_factor_ext_and_all_files()
        builder.add_artifact_pair(source_conc=10, source_vol=10, dilute_factor=None, target_vol=40)

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.execute_short(builder))

    @skip
    def test_capture_output(self):
        # Arrange
        b = ContextBuilder()
        b.with_all_files()
        builder = ExtensionBuilder.create_with_factor_extension(b)
        builder.add_artifact_pair(source_conc=10, source_vol=10, dilute_factor=None, target_vol=40)

        try:
            self.execute_short(builder)
        except UsageError:
            self.copy_to_clipboard(b.context.validation_service.messages)
        # Act
        # Assert
        self.assertEqual(1, 2)

    def test___with_one_transfer_exceeding_source_volume___warning(self):
        # Arrange
        builder = self.builder_with_factor_ext_and_all_files()
        builder.add_artifact_pair(source_conc=10, source_vol=10, dilute_factor=3, target_vol=40)

        # Act
        self.execute_short(builder)

        # Assert
        messages = list(builder.context_builder.context.validation_service.messages)
        print(messages)
        self.assertEqual(1, len(messages))
        self.assertTrue("Volume from sample exceeds current sample volume" in messages[0])
