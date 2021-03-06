from unittest import skip
from clarity_ext import utils
from clarity_ext.domain.container import Container
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.extension_builders import ExtensionInitializer
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestDilutionLibrary(TestDilutionBase):

    def test_target_are_tubes__with_1_input_artifact__pipetting_volumes_ok(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(1, len(transfers))
        self.assertEqual(5, transfers[0].pipette_sample_volume)
        self.assertEqual(5, transfers[0].pipette_buffer_volume)

    def test_target_are_tubes__with_1_input_artifact__destination_barcode_is_numeric(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual('1211111111', transfers[0].target_slot.container.id)

    def test_target_are_tubes__with_2_input_artifacts__2nd_artifact_placed_in_tuberack1(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="targettube1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="targettube2")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(2, len(transfers))
        self.assertEqual("in-FROM:source1-B:1", transfers[1].source_location.artifact.name)
        self.assertEqual(2, transfers[1].source_location.index_down_first)
        self.assertEqual("DNA1", transfers[1].source_slot.name)
        self.assertEqual("out-FROM:source1-B:1", transfers[1].target_location.artifact.name)
        self.assertEqual(2, transfers[1].target_location.index_down_first)
        self.assertEqual("END1", transfers[1].target_slot.name)
        self.assertEqual('Destination-Tuberack1', transfers[1].target_location.container.name)

    def test_target_are_plates__with_2_input_artifacts__2nd_artifact_placed_in_plate1(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(2, len(transfers))
        self.assertEqual("in-FROM:source1-B:1", transfers[1].source_location.artifact.name)
        self.assertEqual(2, transfers[1].source_location.index_down_first)
        self.assertEqual("DNA1", transfers[1].source_slot.name)
        self.assertEqual("out-FROM:source1-B:1", transfers[1].target_location.artifact.name)
        self.assertEqual(2, transfers[1].target_location.index_down_first)
        self.assertEqual("END1", transfers[1].target_slot.name)
        self.assertEqual('target1', transfers[1].target_location.container.name)

    def test_target_tubes__with_one_intermediate_required__number_entries_in_files_ok(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        default_batch = utils.single([b for b in batches if b.name == "default"])
        # self.save_robot_files_to_harddisk(builder, r'/home/edvard/smajobb/2020/januari/clarity/saves')
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len(loop_batch.transfers))
        self.assertEqual(1, len(default_batch.transfers))

    def test_target_tubes__with_one_intermediate_required__pipette_volumes_ok(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")

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

    def test_target_tubes__with_one_intermediate_required__intermediate_is_plate(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        loop_batch = utils.single([b for b in batches if b.name == "looped"])
        transfer_loop = utils.single(loop_batch.transfers)
        target_container_type = transfer_loop.target_location.container.container_type
        self.assertEqual(Container.CONTAINER_TYPE_96_WELLS_PLATE, target_container_type)
        self.assertEqual(8, transfer_loop.target_location.container.size.height)
        self.assertEqual(12, transfer_loop.target_location.container.size.width)

    def test_target_tubes__with_one_intermediate_required__final_placed_in_tuberack(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        default_batch = utils.single([b for b in batches if b.name == "default"])
        transfer_default = utils.single(default_batch.transfers)
        self.assertEqual('Destination-Tuberack1', transfer_default.target_location.container.name)

    def test_target_tubes__with_one_evap_required__number_entries_in_files_ok(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        self.assertEqual(2, len(batches))
        self.assertEqual(1, len(evap1_batch.transfers))
        self.assertEqual(1, len(evap2_batch.transfers))

    def test_target_tubes__with_one_evap_required__intermediate_is_tuberack(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap1_batch = utils.single([b for b in batches if b.name == "evaporate1"])
        transfer_intermediate = utils.single(evap1_batch.transfers)
        self.assertEqual('Destination-Tuberack1', transfer_intermediate.target_location.container.name)

    def test_target_tubes__with_one_evap_required__final_is_tuberack(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        batches = builder.extension.dilution_session.transfer_batches(self.biomek_robot_setting.name)
        evap2_batch = utils.single([b for b in batches if b.name == "evaporate2"])
        transfer_final = utils.single(evap2_batch.transfers)
        self.assertEqual('Destination-Tuberack1', transfer_final.target_location.container.name)

    def test_target_tubes__with_one_destination_tube__slot_container_name_ok(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        # ordinary samples
        builder.add_artifact_pair(source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        # self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        default_batch = builder.default_batch
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual('Destination-Tuberack1', default_batch.target_container_slots[0].container.name)

    def test_target_tubes__with_one_destination_tube__artifact_view_name_ok(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        # ordinary samples
        builder.add_artifact_pair(source_container_name="source1", target_container_name="tube1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        default_batch = builder.default_batch
        transfer_final = utils.single(default_batch.transfers)
        self.assertEqual("out-FROM:source1-A:1", transfer_final.target_location.artifact.view_name)

    def test_target_plates__with_one_destination_artifact__artifact_view_name_is_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_library_dil_extension()
        # ordinary samples
        builder.add_artifact_pair(source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        default_batch = builder.default_batch
        transfer_final = utils.single(default_batch.transfers)
        self.assertEqual("out-FROM:source1-A:1", transfer_final.target_location.artifact.view_name)

    def test_target_are_tubes__with_four_artifacts__destination_order_ok(self):
        # Arrange
        initz = ExtensionInitializer()
        initz.with_target_container_type(Container.CONTAINER_TYPE_TUBE)
        initz.with_source_well_positions_from_first(False)
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            initz)
        builder.add_artifact_pair(source_container_name="source9", target_container_name="tube1")
        builder.add_artifact_pair(source_container_name="source9", target_container_name="tube2")
        builder.add_artifact_pair(source_container_name="source10", target_container_name="tube3")
        builder.add_artifact_pair(source_container_name="source10", target_container_name="tube4")

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        transfer1 = transfers[0]
        transfer2 = transfers[1]
        transfer3 = transfers[2]
        transfer4 = transfers[3]
        self.assertEqual(1, transfer1.target_location.index_down_first)
        self.assertEqual(2, transfer2.target_location.index_down_first)
        self.assertEqual(3, transfer3.target_location.index_down_first)
        self.assertEqual(4, transfer4.target_location.index_down_first)

    def test_target_are_tubes__with_one_artifact_destination_volume_300__number_transfers_are_6(self):
        # Arrange
        builder = self._create_builder_with_tubes()
        builder.add_artifact_pair(source_container_name="source1", target_container_name="target1",
                                  target_vol=300)

        # Act
        self.execute_short(builder)

        # Assert
        transfers = builder.sorted_transfers
        self.assertEqual(6, len(transfers))
        self.assertEqual(30, transfers[0].pipette_sample_volume)
        self.assertAlmostEqual(45, transfers[0].pipette_buffer_volume, 1)
        self.assertEqual(0, transfers[1].pipette_sample_volume)
        self.assertAlmostEqual(45, transfers[5].pipette_buffer_volume, 1)

    def test__with_fixed_sample_transfer__min_volume_adjusted_for_next_dilution(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_shared_result_file('Step log', existing_file_name='Warnings')
        context_builder.with_udf_on_step('Min pipette volume (ul)', 4)
        context_builder.with_udf_on_step('Max scale up volume (ul)', 50)
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            context_builder=context_builder)
        builder.add_artifact_pair(
            source_conc=10, target_conc=10, target_vol=4,
            source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        batch = builder.default_batch
        transfer = utils.single(batch.transfers)
        self.assertEqual(5, transfer.pipette_sample_volume)
        self.assertEqual(0, transfer.pipette_buffer_volume)

    def test__with_buffer_volume_almost_zero__min_volume_adjusted_for_next_dilution(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_shared_result_file('Step log', existing_file_name='Warnings')
        context_builder.with_udf_on_step('Min pipette volume (ul)', 4)
        context_builder.with_udf_on_step('Max scale up volume (ul)', 50)
        builder = ExtensionBuilderFactory.create_with_library_dil_extension(
            context_builder=context_builder)
        builder.add_artifact_pair(
            source_conc=10, target_conc=9, target_vol=4,
            source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        # self.save_robot_files_to_harddisk(builder, r'/home/edvard/smajobb/2020/januari/clarity/saves')
        batch = builder.default_batch
        transfer = utils.single(batch.transfers)
        self.assertAlmostEqual(5.0, transfer.pipette_sample_volume, 1)
        self.assertAlmostEqual(0.56, transfer.pipette_buffer_volume, 2)

    def _create_builder_with_tubes(self, write_to_harddisk=False):
        initz = ExtensionInitializer()
        initz.target_container_type = Container.CONTAINER_TYPE_TUBE
        context_builer = ContextBuilder()
        if write_to_harddisk:
            context_builer.with_all_files()
        return ExtensionBuilderFactory.create_with_library_dil_extension(initz, context_builer)
