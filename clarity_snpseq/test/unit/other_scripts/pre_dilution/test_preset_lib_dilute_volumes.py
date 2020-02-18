import unittest
from clarity_ext_scripts.dilution.preset_lib_dilution import Extension as PresetLibDilution
from clarity_ext_scripts.dilution.preset_lib_dilution import PresetValidator
from clarity_ext.utils import single
from clarity_snpseq.test.utility.higher_level_builders.pre_dilution_extension_builder import PreDilutionExtensionBuilder
from clarity_ext.domain.validation import UsageError


class TestPresetLibDiluteValues(unittest.TestCase):
    def setUp(self):
        self.builder = PreDilutionExtensionBuilder()
        self.builder.create(PresetLibDilution)

    def test__with_novaseq_s1_xp__target_volume_is_30(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'novaseq_s1_xp',
            pooling='1 lib/pool', seq_instrument='Novaseq S1', number_of_lanes='1 lane/pool',
            conc_fc='200')

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(30, pair.output_artifact.udf_target_vol_ul)

    def test__with_miseq__target_volume_is_14(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'miseq',
            pooling='1 lib/pool', seq_instrument='miseq', number_of_lanes='1 lane/pool')

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(14, pair.output_artifact.udf_target_vol_ul)

    def test_pool__with_novaseq_s1_xp__target_volume_is_30(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'novaseq_s1_xp',
            pooling=None, seq_instrument='Novaseq S1', number_of_lanes='1 lane/pool',
            number_samples=3, conc_fc='200'
        )

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(30, pair.output_artifact.udf_target_vol_ul)

    def test__with_target_value_float(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'novaseq_s1_xp',
            pooling='7 libraries/pool', seq_instrument='Novaseq S1',
            number_of_lanes='1 lane/pool', conc_fc='200')

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertAlmostEqual(4.29, pair.output_artifact.udf_target_vol_ul, places=2)

    def test_prep_sample__without_pooling_udf__usage_error(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Errors')
        self.builder.create_pair(
            '1234', 'novaseq_s1_xp',
            pooling=None, seq_instrument='Novaseq S1', number_of_lanes='1 lane/pool')

        # Act
        # Assert
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

    def test__with_instrument_combination_not_present_in_table__warning(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Warnings')
        self.builder.create_pair(
            '1234', 'combination_not_present',
            pooling='1 lib/pool', seq_instrument='Novaseq S3', number_of_lanes='1 lane/pool',
            conc_fc='200')

        # Act
        self.builder.extension.execute()

        # Assert
        warning_count = self.builder.context_builder.context.validation_service.warning_count
        self.assertEqual(1, warning_count)

    def test__with_pooling_udf_without_number__usage_error(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Errors')
        self.builder.create_pair(
            '1234', 'novaseq_s1_xp',
            pooling='lib/pool', seq_instrument='Novaseq S1', number_of_lanes='1 lane/pool')

        # Act
        # Assert
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

    def test_validate_pooling_correct_values(self):
        valid_values = [
            '1 lib/pool',
            '1 library/pool',
            '2 libraries/pool',
            '2 libraries / pool '
            '2 lib / pool',
            '1lib/pool'
        ]
        pair = self.builder.create_pair('1', 'name')

        for value in valid_values:
            validator = PresetValidator(None, None, None, None, None)
            validator._validate_pooling_udf(pair.output_artifact, value)

    def test_validate_pooling_udf__with_not_correct_value__exception_cast(self):
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Errors')
        self.builder.create_pair(
            '1234', 'not_correct', pooling='2 libs/pool',
            seq_instrument='Novaseq S1', number_of_lanes='1 lane/pool')
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

    @unittest.skip('')
    def test_validate_pooling__not_correct_values__exception_cast(self):
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Errors')
        not_valid_values = [
            '2 libs/pool',
            '2.3 lib/pool',
            '1 pool/lib',
            'library/pool'
        ]
        for value in not_valid_values:
            builder = PreDilutionExtensionBuilder()
            builder.create(PresetLibDilution)
            builder.create_pair(
                '1234', 'novaseq_s1_xp',
                pooling=value, seq_instrument='Novaseq S1', number_of_lanes='1 lane/pool')
            with self.assertRaises(UsageError):
                self.builder.extension.execute()

    def test_parse_pooling_udf__correct_value(self):
        pooling = '3 libraries/pool'
        lib_per_pool = self.builder.extension._parse_pooling_udf(pooling)
        self.assertEqual(3, lib_per_pool)

    def test__with_instrument_3_words__exception(self):
        self.builder.context_builder.with_shared_result_file('Step log', '8908', 'Errors')
        self.builder.create_pair(
            '1234', 'not correct', pooling='2 lib/pool', seq_instrument='novaseq s1 xp',
            number_of_lanes='1 lane/pool')
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

    def test__with_instrument_empty__exception(self):
        self.builder.context_builder.with_shared_result_file('Step log', '8908', 'Errors')
        self.builder.create_pair(
            '1234', 'not correct', pooling='2 lib/pool',
            number_of_lanes='1 lane/pool', seq_instrument=None)
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

    def test__flowcell_type_not_correct__exception(self):
        self.builder.context_builder.with_shared_result_file('Step log', '8908', 'Errors')
        self.builder.create_pair(
            '1234', 'not correct', pooling='2 lib/pool',
            number_of_lanes='1 xxx/pool', seq_instrument='NovaSeq S1')
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

    def test__with_novaseq_s1_xp_and_20_samples_in_pool__target_volume_is_scaled_up_to_2(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'novaseq_s1_xp',
            pooling='20 lib/pool', seq_instrument='Novaseq S1', number_of_lanes='1 lane/pool',
            conc_fc='200')

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(2, pair.output_artifact.udf_target_vol_ul)
