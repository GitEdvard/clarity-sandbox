import unittest
from clarity_ext_scripts.dilution.preset_lib_dilution import Extension as PresetLibDilution
from clarity_ext_scripts.dilution.preset_lib_dilution import PresetValidator
from clarity_ext.utils import single
from clarity_snpseq.test.utility.higher_level_builders.pre_dilution_extension_builder import PreDilutionExtensionBuilder
from clarity_ext.domain.validation import UsageError


class TestPresetLibDiluteConc(unittest.TestCase):
    def setUp(self):
        self.builder = PreDilutionExtensionBuilder()
        self.builder.create(PresetLibDilution)

    def test_with_miseq_sample__target_conc_is_2_nm(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'miseq',
            pooling='1 lib/pool', seq_instrument='MiSeq', number_of_lanes='1 lane/pool')

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(2, pair.output_artifact.udf_target_conc_nm)

    def test_with_iseq_sample__target_conc_is_1_nm(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'miseq',
            pooling='1 lib/pool', seq_instrument='iSeq', number_of_lanes='1 lane/pool')

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(1, pair.output_artifact.udf_target_conc_nm)

    def test_with_unknown_instrument__warning(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Warnings')
        self.builder.create_pair(
            '1234', 'iSeq',
            pooling='1 lib/pool', seq_instrument='xxx', number_of_lanes='1 lane/pool')

        # Act
        self.builder.extension.execute()

        # Assert
        warning_count = self.builder.context_builder.context.validation_service.warning_count
        self.assertEqual(2, warning_count)

    def test_with_novaseq_sample__conc_fc_is_numeric__target_conc_is_5_x_conc_fc(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'NovaSeq',
            pooling='1 lib/pool', seq_instrument='NovaSeq S1', number_of_lanes='1 lane/pool',
            conc_fc='200'
        )

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(1, pair.output_artifact.udf_target_conc_nm)

    def test_with_novaseq_sample__conc_fc_textual__target_conc_is_5_x_conc_fc(self):
        # Arrange
        self.builder.create_pair(
            '1234', 'NovaSeq',
            pooling='1 lib/pool', seq_instrument='NovaSeq S1', number_of_lanes='1 lane/pool',
            conc_fc='200 pM'
        )

        # Act
        self.builder.extension.execute()

        # Assert
        pairs = self.builder.all_aliquot_pairs
        pair = single(pairs)
        self.assertEqual(1, pair.output_artifact.udf_target_conc_nm)

    def test_with_novaseq_sample__no_warning(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Warnings')
        self.builder.create_pair(
            '1234', 'iSeq',
            pooling='1 lib/pool', seq_instrument='NovaSeq S1', number_of_lanes='1 lane/pool',
            conc_fc='200'
        )

        # Act
        self.builder.extension.execute()

        # Assert
        warning_count = self.builder.context_builder.context.validation_service.warning_count
        self.assertEqual(0, warning_count)

    def test_with_novaseq_and_no_conc_fc__error(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Errors')
        self.builder.create_pair(
            '1234', 'iSeq',
            pooling='1 lib/pool', seq_instrument='NovaSeq S1', number_of_lanes='1 lane/pool'
        )

        # Act
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

        # Assert
        error_count = self.builder.context_builder.context.validation_service.error_count
        self.assertEqual(1, error_count)

    def test_with_novaseq_and_conc_fc_is_not_parsable__error(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Errors')
        self.builder.create_pair(
            '1234', 'iSeq',
            pooling='1 lib/pool', seq_instrument='NovaSeq S1', number_of_lanes='1 lane/pool',
            conc_fc='1 nM'
        )

        # Act
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

        # Assert
        error_count = self.builder.context_builder.context.validation_service.error_count
        self.assertEqual(1, error_count)

    def test_with_inconsistent_pool_udf_values__validation_error(self):
        # Arrange
        self.builder.context_builder.with_shared_result_file('Step log', '7897', 'Errors')
        self.builder.context_builder.with_shared_result_file('Step log', '7896', 'Warnings')
        from clarity_snpseq.test.utility.pair_builders import SampleBuilder
        sample_builder = SampleBuilder()
        sample_builder.with_udf('Sequencing instrument', 'novaseq')
        sample_builder.with_udf('Number of lanes', '1 lane/pool')
        sample_builder.with_udf('conc FC', '200')
        sample1 = sample_builder.create()
        sample_builder = SampleBuilder()
        sample_builder.with_udf('Sequencing instrument', 'novaseq')
        sample_builder.with_udf('Number of lanes', None)
        sample_builder.with_udf('conc FC', '200')
        sample2 = sample_builder.create()
        samples = [sample1, sample2]

        self.builder.create_pair_from_samples('1234', 'pool_incosistent', samples)

        # Act
        with self.assertRaises(UsageError):
            self.builder.extension.execute()

        # Assert
        error_count = self.builder.context_builder.context.validation_service.error_count
        self.assertEqual(1, error_count)
