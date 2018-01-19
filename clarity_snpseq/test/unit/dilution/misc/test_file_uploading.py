import unittest
from clarity_ext import utils
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_ext.domain.validation import UsageError


class TestFileUploading(TestDilutionBase):
    def test__with_one_ordinary_sample__two_file_handles(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_single()

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(2, len(builder.mocked_file_service.file_handles))

    def test__with_one_ordinary_sample__file_handle_names_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_single()

        # Act
        builder.extension.execute()

        # Assert
        file_handles = builder.mocked_file_service.file_handles
        self.assertEqual("Final", file_handles[0])
        self.assertEqual("Metadata", file_handles[1])

    def test__with_one_ordinary_sample__two_driver_files_in_final(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_single()

        # Act
        builder.extension.execute()

        # Assert
        driver_files = [tuple for tuple in builder.mocked_file_service.file_handle_name_tuples
                        if tuple[0] == "Final"]
        self.assertEqual(2, len(driver_files))

    def test__with_one_evap_sample__tree_file_handles(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_single()

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(3, len(builder.mocked_file_service.file_handles))

    def test__with_one_evap_sample__file_handle_names_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # evaporation sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_single()

        # Act
        builder.extension.execute()

        # Assert
        file_handles = builder.mocked_file_service.file_handles
        self.assertEqual("Evaporate step 1", file_handles[0])
        self.assertEqual("Evaporate step 2", file_handles[1])
        self.assertEqual("Metadata", file_handles[2])

    def test__with_one_looped_sample__three_file_handles(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_single()

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(3, len(builder.mocked_file_service.file_handles))

    def test__with_one_looped_sample__file_handle_names_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")
        builder.monkey_patch_upload_single()

        # Act
        builder.extension.execute()

        # Assert
        file_handles = builder.mocked_file_service.file_handles
        self.assertEqual("Final", file_handles[0])
        self.assertEqual("Intermediate", file_handles[1])
        self.assertEqual("Metadata", file_handles[2])

    def test__with_one_ordinary_sample__robot_file_found_in_upload_cache(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        upload_cache = builder.context_wrapper.context.file_service.artifactid_by_filename
        default_batch = builder.default_batch
        self.assertTrue(default_batch.driver_file.file_name in upload_cache)
        #self.assertEqual("0", upload_cache[default_batch.driver_file.file_name])

    def test__with_one_ordinary_sample__driver_file_name_in_metadata_ok(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.with_mocked_file_service()
        # ordinary sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        metadata_info = builder.metadata_info("metadata_filename", self.hamilton_robot_setting)
        file_name = utils.single([tb.upload_file_name for tb in metadata_info.transfer_batches])
        self.assertEqual("92-1_hamilton", file_name[:13])
