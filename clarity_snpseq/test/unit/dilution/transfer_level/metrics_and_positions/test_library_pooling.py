from unittest import skip
from clarity_ext import utils
from clarity_ext.domain.container import PlateSize
from pprint import pprint
from clarity_ext.domain.container import Container
from clarity_ext.service.dilution.service import SortStrategy
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.extension_builders import ExtensionInitializer


class TestLibraryPooling(TestDilutionBase):
    def test__with_2_input_samples_and_1_pool__positions_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]
        self.assertEqual('Pool1', transfer1.target_location.artifact.container.name)
        self.assertEqual('Pool1', transfer2.target_location.artifact.container.name)
        self.assertEqual('Destination-Tuberack1', transfer1.target_location.container.name)
        self.assertEqual('Destination-Tuberack1', transfer2.target_location.container.name)
        self.assertEqual('DNA1', transfer1.source_slot.name)
        self.assertEqual('DNA1', transfer2.source_slot.name)
        self.assertEqual(1, transfer1.source_location.index_down_first)
        self.assertEqual(2, transfer2.source_location.index_down_first)
        self.assertEqual('END1', transfer1.target_slot.name)
        self.assertEqual('END1', transfer2.target_slot.name)
        self.assertEqual(1, transfer1.target_location.index_down_first)
        self.assertEqual(1, transfer2.target_location.index_down_first)

    def test__with_4_input_samples_and_2_pools__1st_sample_in_2nd_pool_positions_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=2, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=2, conc=10, vol=50, container_name='source1')
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.add_pool(pool_nr=2, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)
        # builder.extension.execute()

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer3 = sorted_transfers[2]
        self.assertEqual(3, transfer3.source_location.index_down_first)
        self.assertEqual('END1', transfer3.target_slot.name)
        self.assertEqual(2, transfer3.target_location.index_down_first)

    def test__with_4_input_samples_and_2_pools__pool_sort_order_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=2, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=2, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='source1')
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.add_pool(pool_nr=2, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)
        # builder.extension.execute()

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]
        transfer3 = sorted_transfers[2]
        transfer4 = sorted_transfers[3]
        self.assertEqual(2, transfer1.target_location.index_down_first)
        self.assertEqual(2, transfer2.target_location.index_down_first)
        self.assertEqual(1, transfer3.target_location.index_down_first)
        self.assertEqual(1, transfer4.target_location.index_down_first)

    def test__with_2_input_in_tubes_and_1_pool__positions_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.source_container_type = Container.CONTAINER_TYPE_TUBE
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube2')
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]
        self.assertEqual('Pool1', transfer1.target_location.artifact.container.name)
        self.assertEqual('Pool1', transfer2.target_location.artifact.container.name)
        self.assertEqual('Source-Tuberack1', transfer1.source_location.container.name)
        self.assertEqual('Source-Tuberack1', transfer2.source_location.container.name)
        self.assertEqual('Destination-Tuberack1', transfer1.target_location.container.name)
        self.assertEqual('Destination-Tuberack1', transfer2.target_location.container.name)
        self.assertEqual('DNA1', transfer1.source_slot.name)
        self.assertEqual('DNA1', transfer2.source_slot.name)
        self.assertEqual(1, transfer1.source_location.index_down_first)
        self.assertEqual(2, transfer2.source_location.index_down_first)
        self.assertEqual('END1', transfer1.target_slot.name)
        self.assertEqual('END1', transfer2.target_slot.name)
        self.assertEqual(1, transfer1.target_location.index_down_first)
        self.assertEqual(1, transfer2.target_location.index_down_first)

    def test__with_2_input_in_tubes_and_1_pool__two_occupied_in_source_tuberack(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.source_container_type = Container.CONTAINER_TYPE_TUBE
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube2')
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        transfer1 = final_batch.transfers[0]
        source_tube_rack = transfer1.source_location.container
        self.assertEqual(2, len(source_tube_rack.occupied))

    def test__with_2_input_tubes_and_1_pool__source_tuberack_included_in_metadata(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.source_container_type = Container.CONTAINER_TYPE_TUBE
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube2')
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer2 = sorted_transfers[1]
        self.assertTrue(transfer2.source_slot.include_in_metadata)

    def test__with_1_input_tube_and_phix__phix_excluded_in_robotfile(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.source_container_type = Container.CONTAINER_TYPE_TUBE
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube2')
        builder.add_input_phix(pool_nr=1)
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        self.assertEqual(2, len(final_batch.driver_file.data))

    def test__with_1_input_tube_and_phix__phix_excluded_in_tuberack(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.source_container_type = Container.CONTAINER_TYPE_TUBE
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        builder = ExtensionBuilderFactory.create_with_library_pooling(initz)
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube1')
        builder.add_input_artifact(pool_nr=1, conc=10, vol=50, container_name='tube2')
        builder.add_input_phix(pool_nr=1)
        builder.add_pool(pool_nr=1, target_vol=20)
        builder.assemble_pairs()

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        source_tube_rack = transfer1.source_location.container
        self.assertEqual(2, len(source_tube_rack.occupied))
        self.assertFalse([well for well in source_tube_rack.occupied if well.artifact.name == 'PhiX'])
