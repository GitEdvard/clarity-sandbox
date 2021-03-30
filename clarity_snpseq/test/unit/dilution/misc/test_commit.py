
from unittest import skip
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_ext.domain.validation import UsageError


class CommitTests(TestDilutionBase):
    def test_commit__with_normal_dilution__5_files_uploaded(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_mocked_step_log_service()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()
        builder.extension.context.file_service.commit(disable_commits=True)

        # Assert
        # Use file_service -> logger for sensing
        messages = builder.extension.context.file_service.logger.info_messages
        uploads = [m for m in messages if 'Uploading (disabled) file:' in m]
        print(uploads)
        self.assertEqual(5, len(uploads))

    def test_commit__with_normal_dilution__2_uploaded_files_is_for_hamilton(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_mocked_step_log_service()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()
        builder.extension.context.file_service.commit(disable_commits=True)

        # Assert
        # Use file_service -> logger for sensing
        messages = builder.extension.context.file_service.logger.info_messages
        commit_uploads = [m for m in messages if 'Uploading (disabled) file:' in m]
        hamilton_uploads = [m for m in commit_uploads if 'hamilton' in m.lower()]
        self.assertEqual(2, len(hamilton_uploads))

    def test_commit__with_normal_dilution__2_uplaoded_files_is_for_biomek(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_mocked_step_log_service()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()
        builder.extension.context.file_service.commit(disable_commits=True)

        # Assert
        # Use file_service -> logger for sensing
        messages = builder.extension.context.file_service.logger.info_messages
        commit_uploads = [m for m in messages if 'Uploading (disabled) file:' in m]
        biomek_uploads = [m for m in commit_uploads if 'biomek' in m.lower()]
        self.assertEqual(2, len(biomek_uploads))

    def test_commit__with_dilution_has_usage_error__two_step_logs_uploaded(self):
        # Ordinary step log and error step log is uploaded
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_mocked_step_log_service()
        # ordinary sample, pipette volume too high
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=350,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        try:
            builder.extension.execute()
        except UsageError:
            pass

        builder.extension.context.file_service.commit(disable_commits=True)

        # Assert
        # Use file_service -> logger for sensing
        messages = builder.extension.context.file_service.logger.info_messages
        commit_uploads = [m for m in messages if 'Uploading (disabled) file:' in m]
        steplog_uploads = [m for m in commit_uploads if 'step_log' in m.lower()]
        self.assertEqual(2, len(steplog_uploads))

    def test_commit__with_normal_dilution__printouts_from_commit(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.with_mocked_step_log_service()
        # Ordinary sample
        builder.add_artifact_pair(source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        builder.extension.execute()
        builder.extension.context.file_service.commit(disable_commits=True)

        # Assert
        # Set to fail to see printouts
        self.assertEqual(1, 1)
