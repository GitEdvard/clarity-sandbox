from unittest import skip
from clarity_ext import utils
from clarity_ext.domain.container import PlateSize
from clarity_ext.domain.container import Container
from clarity_ext.domain.validation import UsageError
from clarity_ext.service.dilution.service import SortStrategy
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.extension_builders import ExtensionInitializer
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestLibraryPooling(TestDilutionBase):
    def test__with_pool_volume_2000_ul__exception(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_all_files()
        initz = ExtensionInitializer()
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(
            extension_initializer=initz, context_builder=context_builder)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_pool(pool_nr=1, target_vol=2000)
        builder.assemble_pairs()

        # Act
        try:
            self.execute_short(builder)
        except UsageError:
            pass

        # Assert
        error_count = builder.validation_service.error_count
        # it's 2 errors here because of there is 2 input artifacts
        self.assertEqual(2, error_count)

    def test_target_are_pools__with_4x24_plus_4_target_pools__exception(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_all_files()
        initz = ExtensionInitializer()
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(
            extension_initializer=initz, context_builder=context_builder)
        self._add_100_pools(builder)

        # Act
        try:
            self.execute_short(builder)
        except UsageError:
            pass

        # Assert
        error_count = builder.validation_service.error_count
        # it's 2 errors here because of there is 2 input artifacts
        self.assertEqual(1, error_count)

    def _add_100_pools(self, builder):
        for i in range(100):
            builder.add_input_artifact(pool_nr=i + 1, conc=10, vol=50, container_name='source1')
            builder.add_pool(pool_nr=i + 1, target_vol=20)
        builder.assemble_pairs()
