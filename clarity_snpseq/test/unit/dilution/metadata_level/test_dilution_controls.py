import unittest
import datetime
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.settings import HamiltonRobotSettings
from clarity_ext.service.file_service import UploadFileService
from clarity_ext.service.file_service import OSService
from test.unit.clarity_ext.helpers import *
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.utility.helpers import DilutionHelpers


class TestDilution(unittest.TestCase):

    def test_instantiate_dilution2(self):
        conc1 = 22.8
        vol1 = 38
        conc2 = 22
        vol2 = 35

        helper = DilutionHelpers()
        ext_wrapper, dil_helper = helper.create_helpers(ExtensionDna)
        pair = dil_helper.create_dilution_pair(
            conc1=conc1, vol1=vol1, conc2=conc2, vol2=vol2,
            source_type=Analyte, target_type=Analyte)
        ext_wrapper.context_wrapper.add_analyte_pair(pair.input_artifact, pair.output_artifact)
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

    def test__with_two_controls_and_one_normal_sample__examine_variables(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
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
        builder = ExtensionBuilder.create_with_dna_extension()
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

    def test__with_two_previous_added_controls_and_one_normal__controls_included_in_container_mapping(self):
        """
        In this test, lims-id for control artifacts are updated with prefix 2- 
        """
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_control_id_prefix("2-")
        builder.add_artifact_pair(source_container_name="source1")
        builder.add_artifact_pair(source_container_name="control container", is_control=True)
        builder.add_artifact_pair(source_container_name="control container", is_control=True)

        # Act
        builder.extension.execute()

        # Assert
        metadata_info = builder.metadata_info("Metadata filename", HamiltonRobotSettings())
        self.assertTrue("source1" in [m[0].container.name for m in metadata_info.container_mappings])
        self.assertTrue("control container" in [m[0].container.name for m in metadata_info.container_mappings])
