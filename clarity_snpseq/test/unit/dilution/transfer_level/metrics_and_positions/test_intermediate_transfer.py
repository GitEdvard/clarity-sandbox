from unittest import skip
from clarity_ext import utils
from clarity_ext.domain.container import PlateSize
from clarity_ext.domain.container import Container
from clarity_ext.service.dilution.service import SortStrategy
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.extension_builders import ExtensionInitializer
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestIntermediateTransfers(TestDilutionBase):

    def test__with_one_looped__number_entries_in_files_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.context.logger.write_to_stout = True

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len(loop_batch.transfers))
        self.assertEqual(1, len(default_batch.transfers))

    def test__with_one_looped__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_loop = utils.single(loop_batch.transfers)
        transfer_default = utils.single(default_batch.transfers)
        self.assertEqual(4, transfer_loop.pipette_sample_volume)
        self.assertEqual(36, transfer_loop.pipette_buffer_volume)
        self.assertEqual(2, transfer_default.pipette_sample_volume)
        self.assertEqual(8, transfer_default.pipette_buffer_volume)

    def test__with_one_looped__looped_hamilton_driver_file_ok(self):
        # Arrange
        # context_builder = ContextBuilder()
        # context_builder.with_all_files()
        # builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder)
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)
        # builder.extension.execute()

        # Assert
        # self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')
        content = builder.loop_batch.driver_file.to_string(include_header=False)
        self.assertEqual('in-FROM:source1-A:1\t1\tDNA1\t4.0\t36.0\t1\tEND1\tsource1\t1111111111\t0', content)

    def test__with_one_looped__final_hamilton_driver_file_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        content = builder.default_batch.driver_file.to_string(include_header=False)
        self.copy_to_clipboard(content)
        self.assertEqual('in-FROM:source1-A:1-looped\t1\tDNA1\t2.0\t8.0\t1\tEND1\t1111111111\ttarget1\t0', content)

    def test__with_one_looped_one_ordinary__pipette_volumes_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_loop = utils.single(loop_batch.transfers)
        sorted_transfers = sorted(default_batch.transfers, key=self.sort_strategy.input_position_sort_key)
        self.assertEqual(4, transfer_loop.pipette_sample_volume)
        self.assertEqual(36, transfer_loop.pipette_buffer_volume)
        self.assertEqual(2, sorted_transfers[0].pipette_sample_volume)
        self.assertEqual(8, sorted_transfers[0].pipette_buffer_volume)
        self.assertEqual(3, sorted_transfers[1].pipette_sample_volume)
        self.assertEqual(7, sorted_transfers[1].pipette_buffer_volume)

    def test__with_two_looped_one_ordinary__number_entries_in_files_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        self.assertEqual(2, len(batches))
        self.assertEqual(2, len(loop_batch.transfers))
        self.assertEqual(3, len(default_batch.transfers))

    def test__with_two_multistep_samples_from_two_plates_same_pos__two_separate_intermediate_slots(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=1, width=1))
        initz.with_target_container_size(PlateSize(height=1, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)
        # self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

        # Assert
        loop_batch = builder.loop_batch
        self.assertEqual(2, len(loop_batch.target_container_slots))

    def test__with_two_multistep_samples_from_two_plates_same_pos__intermediate_pos_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=1, width=1))
        initz.with_target_container_size(PlateSize(height=1, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        loop_batch = builder.loop_batch
        sorted_transfers = sorted(loop_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]
        self.assertEqual('END1', transfer1.target_slot.name)
        self.assertEqual('END2', transfer2.target_slot.name)

    def test__with_two_multistep_samples_from_two_plates_same_pos__temp_plates_has_num_barcode(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=1, width=1))
        initz.with_target_container_size(PlateSize(height=1, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        loop_batch = builder.loop_batch
        sorted_transfers = sorted(loop_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]

        self.assertEqual('1111111111', transfer1.target_slot.container.id)
        self.assertEqual('1111111112', transfer2.target_slot.container.id)

    def test__with_two_multistep_samples_from_two_plates_same_pos__final_source_pos_is_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=1, width=1))
        initz.with_target_container_size(PlateSize(height=1, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]
        self.assertEqual('DNA1', transfer1.source_slot.name)
        self.assertEqual('Temp1', transfer1.source_slot.container.name)
        self.assertEqual('DNA2', transfer2.source_slot.name)
        self.assertEqual('Temp2', transfer2.source_slot.container.name)

    @skip('real')
    def test__with_four_ordinary_samples__positions_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=2, width=1))
        initz.with_target_container_size(PlateSize(height=2, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source2", target_container_name="target2")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        # self.execute_short(builder)
        self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        transfer2 = sorted_transfers[1]
        transfer3 = sorted_transfers[2]
        transfer4 = sorted_transfers[3]
        self.assertEqual('', transfer4.target_location.artifact.name)

    def test__with_four_samples_of_which_two_are_multistep__1st_transfer_from_temp1_2nd_pos(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=2, width=1))
        initz.with_target_container_size(PlateSize(height=2, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source2", target_container_name="target2")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer1 = sorted_transfers[0]
        self.assertEqual(0, transfer1.source_slot.index)
        self.assertEqual('DNA1', transfer1.source_slot.name)
        self.assertEqual('Temp1', transfer1.source_slot.container.name)
        self.assertEqual('out-FROM:source1-B:1', transfer1.target_location.artifact.name)
        self.assertEqual(2, transfer1.source_location.index_down_first)

    def test__with_four_samples_of_which_two_are_multistep__2nd_transfer_from_temp2_2nd_pos(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=2, width=1))
        initz.with_target_container_size(PlateSize(height=2, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source2", target_container_name="target2")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer2 = sorted_transfers[1]
        self.assertEqual(1, transfer2.source_slot.index)
        self.assertEqual('DNA2', transfer2.source_slot.name)
        self.assertEqual('Temp2', transfer2.source_slot.container.name)
        self.assertEqual('out-FROM:source2-B:1', transfer2.target_location.artifact.name)
        self.assertEqual(2, transfer2.source_location.index_down_first)

    def test__with_four_samples_of_which_two_are_multistep__3rd_transfer_from_source1_1st_pos(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=2, width=1))
        initz.with_target_container_size(PlateSize(height=2, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source2", target_container_name="target2")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer3 = sorted_transfers[2]
        self.assertEqual(2, transfer3.source_slot.index)
        self.assertEqual('DNA3', transfer3.source_slot.name)
        self.assertEqual('source1', transfer3.source_slot.container.name)
        self.assertEqual('out-FROM:source1-A:1', transfer3.target_location.artifact.name)
        self.assertEqual(1, transfer3.source_location.index_down_first)

    def test__with_four_samples_of_which_two_are_multistep__4th_transfer_from_source2_1st_pos(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=2, width=1))
        initz.with_target_container_size(PlateSize(height=2, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=15, target_vol=30,
                                  source_container_name="source2", target_container_name="target2")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)
        # self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

        # Assert
        final_batch = builder.default_batch
        sorted_transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        transfer4 = sorted_transfers[3]
        self.assertEqual(3, transfer4.source_slot.index)
        self.assertEqual('DNA4', transfer4.source_slot.name)
        self.assertEqual('source2', transfer4.source_slot.container.name)
        self.assertEqual('out-FROM:source2-A:1', transfer4.target_location.artifact.name)
        self.assertEqual(1, transfer4.source_location.index_down_first)

    def test__with_25_samples_to_tubes_of_which_2_are_looped__positions_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_target_container_type(Container.CONTAINER_TYPE_TUBE)
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        self._add_25_artifacts(builder)

        # Act
        self.execute_short(builder)
        # self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

        # Assert
        loop_batch = builder.loop_batch
        final_batch = builder.default_batch
        transfers = sorted(final_batch.transfers, key=SortStrategy.input_position_sort_key)
        intermediate_trans1 = transfers[0]
        intermediate_trans2 = transfers[1]
        ordinary_transfer = transfers[2]
        self.assertEqual(2, len(loop_batch.target_container_slots))
        # 1st intermediate sample
        self.assertEqual(0, intermediate_trans1.source_slot.index)
        self.assertEqual('DNA1', intermediate_trans1.source_slot.name)
        self.assertEqual('Temp1', intermediate_trans1.source_slot.container.name)
        self.assertEqual(1, intermediate_trans1.source_location.index_down_first)
        # 2nd intermediate sample
        self.assertEqual(1, intermediate_trans2.source_slot.index)
        self.assertEqual('DNA2', intermediate_trans2.source_slot.name)
        self.assertEqual('Temp2', intermediate_trans2.source_slot.container.name)
        self.assertEqual(1, intermediate_trans2.source_location.index_down_first)
        # An ordinary sample
        self.assertEqual(2, ordinary_transfer.source_slot.index)
        self.assertEqual('DNA3', ordinary_transfer.source_slot.name)
        self.assertEqual('source1', ordinary_transfer.source_slot.container.name)
        self.assertEqual(2, ordinary_transfer.source_location.index_down_first)

    def _add_25_artifacts(self, builder):
        # Looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")
        # Ordinary samples
        for i in range(1, 24):
            target_tube = 'tube{}'.format(i + 1)
            builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                      source_container_name='source1', target_container_name=target_tube)
        # Looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="tube25")

    @skip('real')
    def test_temp_container_cache(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_source_container_size(PlateSize(height=1, width=1))
        initz.with_target_container_size(PlateSize(height=1, width=1))
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(initz)
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source2", target_container_name="target2")

        # Act
        self.execute_short(builder)

        # Assert
        self.assertEqual(2, len(builder.extension.dilution_session.map_temporary_container_by_original))

    def test__with_one_multistep_sample__two_batches(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len([b for b in batches if b.name == "default"]))
        self.assertEqual(1, len([b for b in batches if b.name == "looped"]))

    def test__with_one_multistep_sample__original_source_plate_source_in_looped(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(1,len(looped_batch.target_container_slots))
        self.assertEqual("DNA1", looped_batch.source_container_slots[0].name)
        self.assertEqual("source1", looped_batch.source_container_slots[0].container.name)

    def test__with_one_multistep_sample__temp_plate_as_target_in_looped(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(1,len(looped_batch.target_container_slots))
        self.assertEqual("END1", looped_batch.target_container_slots[0].name)
        self.assertEqual("Temp1", looped_batch.target_container_slots[0].container.name)

    def test__with_one_multistep_sample__two_driver_files(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        files = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name).driver_files
        self.assertEqual(2, len(files))
        self.assertEqual(1, len([key for key in files if str(key) == "looped"]))
        self.assertEqual(1, len([key for key in files if str(key) == "default"]))

    def test__with_one_multistep_sample__temp_plate_as_source_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp1", default_batch.source_container_slots[0].container.name)

    def test__with_one_multistep_sample__original_target_is_target_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("END1", default_batch.target_container_slots[0].name)
        self.assertEqual("target1", default_batch.target_container_slots[0].container.name)

    def test__with_one_multistep_one_ordinary__two_source_plates_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)

        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp1", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source1", default_batch.source_container_slots[1].container.name)

    def test__with_mixed_samples_in_one_source_plate__two_source_plates_in_final(self):
        # Arrange
        # context_builder = ContextBuilder()
        # context_builder.with_all_files()
        # builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder=context_builder)
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary samples
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)
        # builder.extension.execute()

        # Assert
        # self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp1", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source1", default_batch.source_container_slots[1].container.name)

    def test__with_two_multistep_in_separate_plates__one_target_plate_in_looped(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(1, len(looped_batch.target_container_slots))

    def test__with_three_source_plates_number_2_is_looped__slot_positioning_in_final_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source3", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(3, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp1", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source1", default_batch.source_container_slots[1].container.name)
        self.assertEqual("DNA3", default_batch.source_container_slots[2].name)
        self.assertEqual("source3", default_batch.source_container_slots[2].container.name)

    def test__with_three_source_plates_number_1_and_3_is_looped__source_slots_in_looped_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source3", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "looped")
        looped_batch = next(gen)
        self.assertEqual(2, len(looped_batch.source_container_slots))
        self.assertEqual("DNA1", looped_batch.source_container_slots[0].name)
        self.assertEqual("source1", looped_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", looped_batch.source_container_slots[1].name)
        self.assertEqual("source3", looped_batch.source_container_slots[1].container.name)

    def test__with_three_source_plates_number_1_and_3_is_looped__source_slots_in_final_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source2", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source3", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(2, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("Temp1", default_batch.source_container_slots[0].container.name)
        self.assertEqual("DNA2", default_batch.source_container_slots[1].name)
        self.assertEqual("source2", default_batch.source_container_slots[1].container.name)

    def test_one_sample__with_sample_conc_less_than_10xtarget_conc__evaporation_is_not_needed(self):
        # This will not work with a fixed intermediate dilution of 10x
        # Arrange
        from clarity_snpseq.test.utility.misc_builders import ContextBuilder
        context_builder = ContextBuilder()
        context_builder.with_shared_result_file('Step log', existing_file_name='Warnings')
        target_vol = 10
        builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder=context_builder)
        builder.add_artifact_pair(source_conc=6, source_vol=40, target_conc=1, target_vol=target_vol,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        # self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/metadata_output')
        self.execute_short(builder)

        # Assert
        default_batch = builder.default_batch
        transfer = utils.single(default_batch.transfers)

        self.assertGreaterEqual(target_vol, transfer.pipette_sample_volume)

    def test_one_sample_with_sample_conc_less_than_10xtarget_conc__pipette_volumes_ok(self):
        # This will not work with a fixed intermediate dilution of 10x
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_shared_result_file('Step log', existing_file_name='Warnings')
        builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder=context_builder)
        builder.add_artifact_pair(source_conc=6, source_vol=40, target_conc=1, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_loop = utils.single(loop_batch.transfers)
        transfer_default = utils.single(default_batch.transfers)
        self.assertEqual(4, transfer_loop.pipette_sample_volume)
        self.assertEqual(20, transfer_loop.pipette_buffer_volume)
        self.assertEqual(10, transfer_default.pipette_sample_volume)
        self.assertEqual(0, transfer_default.pipette_buffer_volume)
