from unittest import skip
from clarity_ext.utils import single
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestLowPipetteVolumesStrategies(TestDilutionBase):
    def setUp(self):
        super(TestLowPipetteVolumesStrategies, self).setUp()
        self.context_builder = ContextBuilder()
        self.builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            context_builder=self.context_builder)

    def test_dilution_has_low_pipette_volume__end_volume_less_than_scale_up__no_intermediate_dilution(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 10)
        self.builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=50, target_vol=2,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batches = self.builder.extension.dilution_session.transfer_batches(
            self.biomek_robot_setting.name)
        self.assertEqual(1, len(batches))

    def test_scale_up_strategy__pipetting_volumes_ok(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 10)
        self.builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=50, target_vol=2,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        transfer = single(batch.transfers)
        self.assertEqual(2, transfer.pipette_sample_volume)
        self.assertEqual(2, transfer.pipette_buffer_volume)

    def test_scale_up_with_rounding__pipette_volumes_ok(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 1000)
        self.builder.add_artifact_pair(source_conc=10, source_vol=40, target_conc=1, target_vol=2.49,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        transfer = single(batch.transfers)
        self.assertAlmostEqual(2, transfer.pipette_sample_volume, places=1)
        self.assertAlmostEqual(18, transfer.pipette_buffer_volume, places=1)

    def test_scale_up_with_rounding__source_volume_subtraction_ok(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_udf_on_step('Max scale up volume (ul)', 1000)
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            context_builder=context_builder)
        builder.add_artifact_pair(source_conc=10, source_vol=40, target_conc=1, target_vol=2.49,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)
        builder.extension._queue_udf_for_update()

        # Assert
        batch = builder.default_batch
        transfer = single(batch.transfers)
        self.assertEqual(-3, transfer.target_location.artifact.udf_dil_calc_source_vol)

    def test__with_explicit_value_of_min_pipette_volume__on_step_level__pipette_volumes_ok(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 10)
        self.context_builder.with_udf_on_step('Min pipette volume (ul)', 4)
        self.builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=50, target_vol=2,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        transfer = single(batch.transfers)
        self.assertEqual(4, transfer.pipette_sample_volume)
        self.assertEqual(4, transfer.pipette_buffer_volume)

    def test__with_explicit_value_of_min_pipette_volume__on_sample_level__pipette_volumes_ok(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 10)
        self.context_builder.with_udf_on_step('Min pipette volume (ul)', 4)
        self.builder.add_artifact_pair(
            source_conc=100, source_vol=40, target_conc=50, target_vol=2,
            source_container_name="source1", target_container_name="target1",
            min_pipette_volume=3)

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        transfer = single(batch.transfers)
        self.assertEqual(3, transfer.pipette_sample_volume)
        self.assertEqual(3, transfer.pipette_buffer_volume)

    def test__with_artifact_has_min_pipette_volume_udf__shows_in_log(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        builder.add_artifact_pair(
            source_conc=100, source_vol=40, target_conc=50, target_vol=2,
            source_container_name="source1", target_container_name="target1",
            min_pipette_volume=3)
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(2, len(batches))
        logger = builder.context_builder.context.logger
        self.assertEqual(3, len(set(logger.staged_messages)))
        self.assertTrue('Udf \'Min pipette volume (ul)\' specifically set to 3 ul on artifact: out-FROM:source1-A:1'
                        in logger.staged_messages)

    def test__with_step_has_min_pipette_volume_udf__shows_in_log(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_udf_on_step('Min pipette volume (ul)', 8)
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(context_builder=context_builder)
        builder.add_artifact_pair(
            source_conc=100, source_vol=40, target_conc=50, target_vol=2,
            source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(2, len(batches))
        logger = builder.context_builder.context.logger
        self.assertEqual(3, len(set(logger.staged_messages)))
        self.assertTrue('Udf \'Min pipette volume (ul)\' set to 8 ul on step'
                        in logger.staged_messages)
