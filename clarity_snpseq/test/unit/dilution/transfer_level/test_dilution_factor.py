import unittest
from clarity_ext.domain.validation import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder


class TestDilutionFactor(unittest.TestCase):

    def test___with_no_split_rows_not_looped___pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_vol=40, dilute_factor=2, target_vol=10)
        builder.add_artifact_pair(source_vol=40, dilute_factor=3, target_vol=10)
        builder.add_artifact_pair(source_conc=60, source_vol=40, dilute_factor=4, target_vol=10)

        # Act
        builder.extension.execute()

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(5, transfers[0].pipette_sample_volume)
        self.assertEqual(5, transfers[0].pipette_buffer_volume)
        self.assertEqual(3.3, transfers[1].pipette_sample_volume)
        self.assertEqual(6.7, transfers[1].pipette_buffer_volume)
        self.assertEqual(2.5, transfers[2].pipette_sample_volume)
        self.assertEqual(7.5, transfers[2].pipette_buffer_volume)

    def test___without_source_conc___target_conc_is_none(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_vol=40, dilute_factor=4, target_vol=10)

        # Act
        builder.extension.execute()

        # Assert
        update_queue = list(builder.extension.context._update_queue)
        output_artifact = update_queue[0]
        self.assertIsNone(output_artifact.udf_dil_calc_target_conc)

    def test___with_no_split_rows_not_looped___updates_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_conc=80, source_vol=40, dilute_factor=3, target_vol=10)
        # Act
        builder.extension.execute()

        # Assert

        update_queue = list(builder.extension.context._update_queue)
        output_artifact = update_queue[0]

        self.assertEqual(1, len(update_queue))
        self.assertEqual(-4.3, output_artifact.udf_dil_calc_source_vol)
        #self.assertEqual(26.7, round(output_artifact.udf_dil_calc_target_conc, 1))
        self.assertEqual(10, round(output_artifact.udf_dil_calc_target_vol))

    def test___with_split_row___pipette_volume_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_conc=80, source_vol=80, dilute_factor=10, target_vol=80)

        # Act
        builder.extension.execute()

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(2,len(transfers))
        self.assertEqual(8, transfers[0].pipette_sample_volume)
        self.assertEqual(36, transfers[0].pipette_buffer_volume)
        self.assertEqual(0, transfers[1].pipette_sample_volume)
        self.assertEqual(36, transfers[1].pipette_buffer_volume)

    def test___with_split_row___updates_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_conc=80, source_vol=80, dilute_factor=10, target_vol=80)

        # Act
        builder.extension.execute()

        # Assert
        output_artifact = builder.update_queue[0]
        self.assertEqual(-9, output_artifact.udf_dil_calc_source_vol)
        #self.assertEqual(8, round(output_artifact.udf_dil_calc_target_conc, 1))
        self.assertEqual(80, round(output_artifact.udf_dil_calc_target_vol, 1))

    def test___with_single_transfer_looped_dilution___exception_cast(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_vol=80, dilute_factor=35, target_vol=10)

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: builder.extension.execute())

    def test___with_one_transfer_lacking_dilute_factor___exception_cast(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_conc=10, source_vol=10, dilute_factor=None, target_vol=40)

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: builder.extension.execute())

    def test___with_one_transfer_exceeding_source_volume___warning(self):
        # Arrange
        builder = ExtensionBuilder.create_with_factor_extension()
        builder.add_artifact_pair(source_conc=10, source_vol=10, dilute_factor=3, target_vol=40)

        # Act
        builder.extension.execute()

        # Assert
        messages = list(builder.ext_wrapper.context_wrapper.context.validation_service.messages)
        print(messages)
        self.assertEqual(1, len(messages))
        self.assertTrue("Volume from sample exceeds current sample volume" in messages[0])
