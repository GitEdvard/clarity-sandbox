
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestBothEvaporationAndIntermediate(TestDilutionBase):
    def test__with_one_evaporation_one_multistep_one_ordinary__four_batches(self):
        # Arrange
        context_builder = ContextBuilder()
        context_builder.with_all_files()
        builder = ExtensionBuilderFactory.create_with_dna_extension(context_builder=context_builder)
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="27-8473", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="Test-RNA1_PL1_org_210428")
        # evaporation
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        # self.execute_short(builder)
        builder.extension.execute()

        # Assert
        self.save_metadata_to_harddisk(builder, r'/home/edvard/smajobb/saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.assertEqual(4, len(batches))

    def test__with_one_evap_one_multistep_one_ordinary__four_driver_files(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # evaporation
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        files = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name).driver_files
        self.assertEqual(4, len(files))
        self.assertEqual(1, len([key for key in files if str(key) == "evaporate1"]))
        self.assertEqual(1, len([key for key in files if str(key) == "evaporate2"]))
        self.assertEqual(1, len([key for key in files if str(key) == "looped"]))
        self.assertEqual(1, len([key for key in files if str(key) == "default"]))

    def test__with_one_evaporation_one_multistep_one_ordinary__two_source_plates_in_final(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # evaporation
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        #self.save_robot_files_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "default")
        default_batch = next(gen)
        self.print_list(default_batch.source_container_slots, "source slots")
        self.print_list(default_batch.container_mappings, "container mapping")
        self.assertEqual(2, len(default_batch.source_container_slots))

    def test__with_one_evap_one_multistep_one_ordinary__evap_step2_batch_source_slot_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_dna_extension()
        # ordinary
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # multistep
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # evaporation
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        #self.save_robot_files_to_harddisk(builder.extension, r'C:\Smajobb\2017\Augusti\Clarity\saves')
        batches = builder.extension.dilution_session.transfer_batches(self.hamilton_robot_setting.name)
        gen = (b for b in batches if b.name == "evaporate2")
        evap2_batch = next(gen)
        self.print_list(evap2_batch.source_container_slots, "source slots")
        self.print_list(evap2_batch.container_mappings, "container mapping")
        self.assertEqual(1, len(evap2_batch.source_container_slots))
        self.assertEqual("DNA1", evap2_batch.source_container_slots[0].name)
        self.assertEqual("source1", evap2_batch.source_container_slots[0].container.name)
