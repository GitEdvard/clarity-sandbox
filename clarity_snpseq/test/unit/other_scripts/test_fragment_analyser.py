import unittest
from unittest import skip
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextInitializor
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.utility.misc_builders import FakeStepRepoBuilder
from clarity_snpseq.test.utility.pair_builders import FragmentPairBuilder


class TestFragmentAnalyzer(unittest.TestCase):
    def test__with_correct_input__artifact_udf_gqn_is_updated(self):
        # Arrange
        correct_contents = [
            'Sample ID,GQN,Total Conc. (ng/uL)',
            '92-9987_Ladder,4.76,111',
            '92-998_Test-0009-NanoMiseq7,5.48,151'
        ]
        container, pair = self._create_pair(target_artifact_id='92-998')
        builder = self._create_builder(correct_contents,
                                       container, pair)
        # Act
        builder.extension.execute()

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
        builder = self._create_builder(correct_contents,
                                       container, pair)
        # Act
        builder.extension.execute()

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
        builder = self._create_builder(correct_contents,
                                       container, pair)
        # Act
        builder.extension.execute()

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
        builder = self._create_builder(correct_contents,
                                       container, pair)
        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(5.48, pair.output_artifact.udf_gqn)

    def _create_pair(self, target_artifact_id, artifact_name=None):
        artifact_pair_builder = FragmentPairBuilder()
        artifact_pair_builder.with_target_id(target_artifact_id)
        artifact_pair_builder.with_target_container_name('target')
        if artifact_name is not None:
            artifact_pair_builder.with_source_artifact_name(artifact_name)
            artifact_pair_builder.with_target_artifact_name(artifact_name)
        container = artifact_pair_builder.artifact_repo.container_by_name('target')
        pair = artifact_pair_builder.create()
        return container, pair

    def _create_builder(self, quality_table_contents_as_list, container, pair):
        step_repo_builder = FakeStepRepoBuilder()
        step_repo_builder.with_process_udf('volume in destination ul', 5)
        context_initiator = ContextInitializor(step_repo_builder)
        context_builder = ContextBuilder(context_initiator)
        contents = '\n'.join(quality_table_contents_as_list)
        context_builder.with_mocked_local_shared_file('Quality Table (.csv) (required)',
                                                      contents)
        context_builder.with_output_container(container=container)
        context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)
        builder = ExtensionBuilderFactory.create_with_analyze_quality_table(context_builder)
        return builder
