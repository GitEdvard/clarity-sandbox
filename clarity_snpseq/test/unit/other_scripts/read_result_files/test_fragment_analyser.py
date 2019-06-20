import unittest
from unittest import skip
from clarity_snpseq.test.utility.higher_level_builders.read_result_file_builder import ReadResultFileBuilder
from clarity_ext_scripts.fragment_analyzer.analyze_quality_table import Extension as AnalyzeQualityTable


class TestFragmentAnalyzer(unittest.TestCase):
    def setUp(self):
        builder = ReadResultFileBuilder()
        builder.with_analyte_udf('GQN', None)
        builder.with_analyte_udf('FA Total Conc. (ng/uL)', None)
        builder.with_analyte_udf('Dil. calc source vol', None)
        builder.with_process_udf('volume in destination ul', 5)
        builder.with_mocked_local_shared_file('Quality Table (.csv) (required)')
        self.builder = builder

    def _create_pair(self, target_artifact_id, artifact_name=None):
        return self.builder.create_pair(target_artifact_id, artifact_name)

    def _init_builder(self, contents_as_list, container, pair):
        self.builder.create(
            AnalyzeQualityTable, contents_as_list, container, pair)

    def test__with_correct_input__artifact_udf_gqn_is_updated(self):
        # Arrange
        correct_contents = [
            'Sample ID,GQN,Total Conc. (ng/uL)',
            '92-9987_Ladder,4.76,111',
            '92-998_Test-0009-NanoMiseq7,5.48,151'
        ]
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(correct_contents, container, pair)
        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(5.48, pair.output_artifact.udf_gqn)

    @skip('wip')
    def test__with_wacko_input__exception(self):
        # Arrange
        wacko_contents = [
            'fjadsk'
        ]
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(wacko_contents, container, pair)
        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(5.48, pair.output_artifact.udf_gqn)

    def test__with_correct_input__artifact_udf_fa_total_conc_is_updated(self):
        # Arrange
        correct_contents = [
            'Sample ID,GQN,Total Conc. (ng/uL)',
            '92-9987_Ladder,4.76,111',
            '92-998_Test-0009-NanoMiseq7,5.48,151'
        ]
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(correct_contents, container, pair)
        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(151, pair.output_artifact.udf_fa_total_conc_ngul)

    def test__with_correct_input__ladder_udfs_are_not_updated(self):
        # Arrange
        correct_contents = [
            'Sample ID,GQN,Total Conc. (ng/uL)',
            '92-9987_Ladder,4.76,111',
            '92-998_Test-0009-NanoMiseq7,5.48,151'
        ]
        container, pair = self._create_pair(target_artifact_id='92-9987', artifact_name='Ladder')
        self._init_builder(correct_contents, container, pair)
        # Act
        self.builder.extension.execute()

        # Assert
        self.assertIsNone(pair.output_artifact.udf_fa_total_conc_ngul)
        self.assertIsNone(pair.output_artifact.udf_gqn)

    def test__with_input_ladder_missing_lims_id__artifact_has_udf_gqn_updated(self):
        # Arrange
        correct_contents = [
            'Sample ID,GQN,Total Conc. (ng/uL)',
            'Ladder,4.76,111',
            '92-998_Test-0009-NanoMiseq7,5.48,151'
        ]
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(correct_contents, container, pair)
        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(5.48, pair.output_artifact.udf_gqn)
