from unittest import skip
from clarity_ext.utils import single
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestLowPipetteVolumesStrategies(TestDilutionBase):
    def setUp(self):
        super(TestLowPipetteVolumesStrategies, self).setUp()
        self.context_builder = ContextBuilder()
        self.builder = ExtensionBuilderFactory.create_with_dna_extension(
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

    def test_heidur(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 100)
        self.context_builder.with_udf_on_step('Min pipette volume (ul)', 4)
        self.builder.add_artifact_pair(
            source_conc=100, source_vol=40, target_conc=20, target_vol=10,
            source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        transfer = single(batch.transfers)
        self.assertEqual(4, transfer.pipette_sample_volume)
        self.assertEqual(16, transfer.pipette_buffer_volume)

    def test_heidur__with_scale_up__dil_calc_target_vol_is_ok(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 100)
        self.builder.add_artifact_pair(
            source_conc=18, source_vol=40, target_conc=2, target_vol=5,
            source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        transfer = single(batch.transfers)
        self.assertEqual(2, transfer.pipette_sample_volume)
        self.assertEqual(16, transfer.pipette_buffer_volume)
        dil_calc_target_vol = transfer.update_info.target_vol
        self.assertEqual(18, dil_calc_target_vol)

    def test__with_scale_up_and_row_split__pipette_volumes_ok(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 100)
        self.builder.add_artifact_pair(
            source_conc=54, source_vol=40, target_conc=2, target_vol=5,
            source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        self.assertEqual(2, len(batch.transfers))
        sorted_transfers = sorted(
            batch.transfers, key=self.sort_strategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]
        self.assertEqual(2, transfer1.pipette_sample_volume)
        self.assertAlmostEqual(26, transfer1.pipette_buffer_volume, 1)
        self.assertEqual(0, transfer2.pipette_sample_volume)
        self.assertAlmostEqual(26, transfer2.pipette_buffer_volume, 1)
        dil_calc_target_vol = transfer1.update_info.target_vol
        self.assertEqual(54, dil_calc_target_vol)

    def test_heidur__with_too_small_pip_volume__scale_up(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 100)
        self.context_builder.with_udf_on_step('Min pipette volume (ul)', 5)
        self.builder.add_artifact_pair(
            source_conc=6, source_vol=40, target_conc=2, target_vol=14,
            source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        transfer = single(batch.transfers)
        self.assertEqual(5, transfer.pipette_sample_volume)
        self.assertAlmostEqual(10, transfer.pipette_buffer_volume, 1)
        dil_calc_target_vol = transfer.update_info.target_vol
        self.assertEqual(15, dil_calc_target_vol)

    def test_heidur__with_too_small_pip_volume__intermediate(self):
        # Arrange
        self.context_builder.with_udf_on_step('Max scale up volume (ul)', 0)
        self.context_builder.with_udf_on_step('Min pipette volume (ul)', 5)
        self.builder.add_artifact_pair(
            source_conc=6, source_vol=40, target_conc=2, target_vol=14,
            source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(self.builder)

        # Assert
        batch = self.builder.default_batch
        loop_batch = self.builder.loop_batch
        transfer = single(batch.transfers)
        loop_transfer = single(loop_batch.transfers)
        self.assertAlmostEqual(4.7, loop_transfer.pipette_sample_volume, 1)
        self.assertAlmostEqual(9.3, loop_transfer.pipette_buffer_volume, 1)
        self.assertEqual(14, transfer.pipette_sample_volume)
        self.assertAlmostEqual(0, transfer.pipette_buffer_volume)
        dil_calc_target_vol = transfer.update_info.target_vol
        self.assertEqual(14, dil_calc_target_vol)

    def test__with_artifact_has_min_pipette_volume_udf__shows_in_log(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_shared_result_file('Step log', existing_file_name='Warnings')
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            context_builder=context_builder)
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
        context_builder.with_shared_result_file('Step log', existing_file_name='Warnings')
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
