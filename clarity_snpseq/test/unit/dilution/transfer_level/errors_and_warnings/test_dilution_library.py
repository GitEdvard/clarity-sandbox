from unittest import skip
from clarity_ext.domain.container import Container
from clarity_ext.domain.validation import UsageError
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestDilutionLibrary(TestDilutionBase):
    def test_target_are_tubes__with_4x24_plus_4_input_artifacts__exception_1_error(self):
        # Arrange
        builder = self.builder_with_lib_ext_all_files(Container.CONTAINER_TYPE_TUBE)
        self._add_100_artifacts(builder)

        # Act
        try:
            self.execute_short(builder)
        except UsageError:
            pass

        # Assert
        error_count = builder.validation_service.error_count
        warning_count = builder.validation_service.warning_count
        messages = list(builder.validation_service.messages)
        self.assertEqual(1, error_count)
        self.assertEqual(1, len(messages))
        self.assertEqual(0, warning_count)

    def _add_100_artifacts(self, builder):
        for i in range(100):
            source = 'source{}'.format(i + 1)
            target_tube = 'tube{}'.format(i + 1)
            builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                      source_container_name=source, target_container_name=target_tube)

    def test_target_are_tubes__with_destination_volume_2000__exception_with_one_error(self):
        # Arrange
        builder = self.builder_with_lib_ext_all_files(Container.CONTAINER_TYPE_TUBE)
        # ordinary samples
        builder.add_artifact_pair(source_container_name="source1", target_container_name="target1",
                                  target_vol=2000)

        # Act
        try:
            self.execute_short(builder)
        except UsageError:
            pass

        # Assert
        error_count = builder.validation_service.error_count
        messages = list(builder.validation_service.messages)
        self.assertEqual(1, error_count)
        self.assertEqual(1, len(messages))

    def test_target_are_tubes__with_one_artifact_destination_volume_300__number_transfers_are_6(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            target_container_type=Container.CONTAINER_TYPE_TUBE)
        builder.add_artifact_pair(source_container_name="source1", target_container_name="target1",
                                  target_vol=300)

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(6, len(transfers))
        self.assertEqual(30.0, transfers[0].pipette_sample_volume)
        self.assertEqual(45.0, transfers[0].pipette_buffer_volume)
        self.assertEqual(0, transfers[1].pipette_sample_volume)
        self.assertEqual(45.0, transfers[5].pipette_buffer_volume)
