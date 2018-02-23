import unittest
import datetime
from unittest import skip
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.settings import HamiltonRobotSettings
from clarity_ext.service.file_service import OSService
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.utility.helpers import DilutionHelpers


class TestDilution(TestDilutionBase):

    @skip('')
    def test_instantiate_dilution2(self):
        conc1 = 22.8
        vol1 = 38
        conc2 = 22
        vol2 = 35

        helper = DilutionHelpers()
        ext_wrapper, dil_helper = helper.create_helper(ExtensionDna)
        pair = dil_helper.create_dilution_pair(
            conc1=conc1, vol1=vol1, conc2=conc2, vol2=vol2,
            source_type=Analyte, target_type=Analyte)
        ext_wrapper.context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)
        ext_wrapper.extension.execute()

        # Now test that instantiation of dilution_session is ok
        dilution_session = ext_wrapper.extension.dilution_session
        print (dilution_session.pairs[0].input_artifact.__dict__)
        self.assertEqual(1, 1)

    @unittest.skip("Writes to harddisk")
    def test__with_two_controls_and_one_normal_sample__save_file_on_harddisk(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_control_id_prefix("101C-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Arrange save to harddisk
        artifact_service = builder.extension.context.artifact_service
        upload_file_service = UploadFileService(
            OSService(), artifact_service=artifact_service, disable_commits=True,
        upload_dir=r"C:\Smajobb\2017\April\Run clarity\test_runs")

        # Modified code taken from DilutionSession.execute()
        today = datetime.date.today().strftime("%y%m%d")
        metadata_file_handle = "Metadata"
        metadata_files = list()
        dilution_session = builder.extension.dilution_session
        for robot in dilution_session.robot_settings:
            metadata_file_name = "{}_{}_{}_{}.xml".format(robot.name, today, "EE", "1234")
            metadata_files.append((metadata_file_name, builder.extension.generate_metadata_file(robot, metadata_file_name)))

        # Upload the metadata file:
        upload_file_service.upload_files(metadata_file_handle, metadata_files)

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
        print_list(metadata_info.container_mappings, "container_mappings")
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
        print_list(metadata_info.container_mappings, "container_mappings")
        print_list([m[0].container.name for m in metadata_info.container_mappings], "source containers in container_mappings")
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
