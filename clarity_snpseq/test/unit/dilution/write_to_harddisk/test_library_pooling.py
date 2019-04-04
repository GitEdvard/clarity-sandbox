from unittest import skip
from clarity_ext import utils
from clarity_ext.domain.container import PlateSize
from clarity_ext.domain.container import Container
from clarity_ext.service.dilution.service import SortStrategy
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.extension_builders import ExtensionInitializer
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestLibraryPooling(TestDilutionBase):
    @skip('')
    def test__with_4_input_samples_and_2_pools(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_all_files()
        initz = ExtensionInitializer()
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(
            extension_initializer=initz, context_builder=context_builder)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=2, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=2, conc=10, vol=50, container_name='source1')
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.add_pool(pool_nr=2, target_vol=20)
        builder.assemble_pairs()

        # Act
        builder.extension.execute()
        self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

