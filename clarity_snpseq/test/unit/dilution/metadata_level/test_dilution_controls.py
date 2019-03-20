import unittest
from unittest import skip
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_ext_scripts.dilution.settings.file_rendering import HamiltonRobotSettings


class TestDilution(TestDilutionBase):

    @unittest.skip("One single control does not work")
    def test__with_one_single_control__source_slot_ok(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        default_batch = builder.default_batch
        #self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2017\Oktober\clarity\saves')
        self.assertEqual(1, len(default_batch.source_container_slots))

    @unittest.skip("")
    def test__with_two_controls_and_one_normal_sample__examine_variables(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        metadata_info = builder.metadata_info("Metadata filename", HamiltonRobotSettings())
        self.print_list(metadata_info.container_mappings, "container_mappings")
        self.assertEqual(1,1)

    def test__with_two_added_controls_and_one_normal_sample__control_excluded_in_container_mappings(self):
        """
        container_mappings controls what is shown under source containers and target containers
        in the xml metadata file
        
        Negative controls are taken from the through and should not be included in the source 
        container list.
        
        In future there will be a problem with several types of controls! 
        """

        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        metadata_info = builder.metadata_info("Metadata filename", HamiltonRobotSettings())
        self.print_list(metadata_info.container_mappings, "container_mappings")
        self.print_list([m[0].container.name for m in metadata_info.container_mappings], "source containers in container_mappings")
        self.assertTrue("source1" in [m[0].container.name for m in metadata_info.container_mappings])
        self.assertFalse("control container" in [m[0].container.name for m in metadata_info.container_mappings])

    def test__with_two_added_controls_and_one_normal_sample__source_slot_ok(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        default_batch = builder.default_batch
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("DNA1", default_batch.source_container_slots[0].name)
        self.assertEqual("source1", default_batch.source_container_slots[0].container.name)

    def test__with_two_added_controls_one_normal_sample__target_slot_ok(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        default_batch = builder.default_batch
        self.assertEqual(1, len(default_batch.target_container_slots))
        self.assertEqual("END1", default_batch.target_container_slots[0].name)
        self.assertEqual("target1", default_batch.target_container_slots[0].container.name)

    def test__with_two_previous_added_controls_and_one_normal__source_slot_ok(self):
        """
        In this test, lims-id for control artifacts are updated with prefix 2- 
        """
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_control_id_prefix("2-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        metadata_info = builder.metadata_info("Metadata filename", HamiltonRobotSettings())
        default_batch = builder.default_batch
        print("source slots: {}".format(default_batch.source_container_slots))
        self.assertEqual(1, len(default_batch.source_container_slots))
        self.assertEqual("source1",  default_batch.source_container_slots[0].container.name)
