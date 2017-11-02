import unittest
from clarity_ext import utils
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder


class TestFileUploading(TestDilutionBase):
    def test__with_one_ordinary_sample__two_file_handles(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_files()

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(2, len(builder.upload_service.call_stack))

    def test__with_one_ordinary_sample__file_handle_names_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_files()

        # Act
        builder.extension.execute()

        # Assert
        file_handles = [call[0] for call in builder.upload_service.call_stack]
        self.assertEqual("Final", file_handles[0])
        self.assertEqual("Metadata", file_handles[1])

    def test__with_one_ordinary_sample__two_driver_files_in_final(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_files()

        # Act
        builder.extension.execute()

        # Assert
        driver_files = utils.single([call[1] for call in builder.upload_service.call_stack if call[0] == "Final"])
        self.assertEqual(2, len(driver_files))

    def test__with_one_evap_sample__tree_file_handles(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_files()

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(3, len(builder.upload_service.call_stack))

    def test__with_one_evap_sample__file_handle_names_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_files()

        # Act
        builder.extension.execute()

        # Assert
        file_handles = sorted([call[0] for call in builder.upload_service.call_stack])
        self.assertEqual("Evaporate step 1", file_handles[0])
        self.assertEqual("Evaporate step 2", file_handles[1])
        self.assertEqual("Metadata", file_handles[2])

    def test__with_one_looped_sample__three_file_handles(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_files()

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(3, len(builder.upload_service.call_stack))

    def test__with_one_looped_sample__file_handle_names_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_files()

        # Act
        builder.extension.execute()

        # Assert
        file_handles = sorted([call[0] for call in builder.upload_service.call_stack])
        self.assertEqual("Final", file_handles[0])
        self.assertEqual("Intermediate", file_handles[1])
        self.assertEqual("Metadata", file_handles[2])
