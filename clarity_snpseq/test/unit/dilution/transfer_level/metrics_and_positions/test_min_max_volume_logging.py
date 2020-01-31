from clarity_ext.utils import single
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestMinMaxVolumeLogging(TestDilutionBase):
    def test__with_1_plate_and_2_samples__min_and_max_in_logs(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=5,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(1, len(batches))
        logger = builder.context_builder.context.logger
        self.assertEqual(1, len(set(logger.staged_messages)))
        msg = single(list(set(logger.staged_messages)))
        self.assertEqual('target1: min volume 5.0 ul, max volume 10.0 ul.', msg)

    def test__with_2_plates_and_2_samples_each__min_and_max_in_logs(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=5,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target2")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=5,
                                  source_container_name="source1", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(1, len(batches))
        logger = builder.context_builder.context.logger
        self.assertEqual(2, len(set(logger.staged_messages)))
        self.assertTrue('target1: min volume 5.0 ul, max volume 10.0 ul.' in logger.staged_messages)
        self.assertTrue('target2: min volume 5.0 ul, max volume 10.0 ul.' in logger.staged_messages)

    def test__with_1_tube__no_logs_of_min_max(self):
        # Arrange
        from clarity_snpseq.test.utility.extension_builders import ExtensionInitializer
        from clarity_ext.domain.container import Container
        extension_initializer = ExtensionInitializer()
        extension_initializer.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            extension_initializer=extension_initializer)

        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        self.assertEqual(1, len(batches))
        logger = builder.context_builder.context.logger
        self.assertEqual(0, len(set(logger.staged_messages)))
