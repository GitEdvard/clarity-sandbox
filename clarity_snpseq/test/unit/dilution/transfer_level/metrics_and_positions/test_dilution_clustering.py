from unittest import skip
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class TestDilutionClustering(TestDilutionBase):
    def test_clustering__with_one_input_pair__source_and_target_artifacts_names_unchanged(self):
        # Arrange
        # context_builder = ContextBuilder()
        # context_builder.with_all_files()
        # builder = ExtensionBuilder.create_with_clustering_extension(context_builder=context_builder)
        builder = ExtensionBuilderFactory.create_with_clustering_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)
        # builder.extension.execute()
        # self.save_metadata_to_harddisk(builder.extension, r'C:\Smajobb\2018\Januari\clarity\saves')

        # Assert
        self.assertEqual(1, len(builder.sorted_transfers))
        self.assertEqual('out-FROM:A:1', builder.sorted_transfers[0].target_location.artifact.name)
        self.assertEqual('in-FROM:A:1', builder.sorted_transfers[0].source_location.artifact.name)

    def test_clustering__with_one_input_pair__view_names_are_augmented_with_flowcell_name(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_clustering_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        self.assertEqual(1, len(builder.sorted_transfers))
        self.assertEqual('target1: out-FROM:A:1', builder.sorted_transfers[0].target_location.artifact.view_name)
        self.assertEqual('target1: in-FROM:A:1', builder.sorted_transfers[0].source_location.artifact.view_name)

    def test_clustering__with_one_input_pair__hamilton_robot_driver_file_ok(self):
        # Arrange

        builder = ExtensionBuilderFactory.create_with_clustering_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        contents = builder.default_batch.driver_file.to_string(include_header=False)
        self.assertEqual('target1: in-FROM:A:1\t1\tDNA1\t5.0\t0.0\t1\tEND1\tsource1\t1111111111\t0', contents)

    def test_clustering__with_one_input_pair__biomek_robot_driver_file_ok(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_clustering_extension()
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                                  source_container_name="source1", target_container_name="target1")
        # Act
        self.execute_short(builder)

        # Assert
        default_batch_biomek = next(builder.get_from_biomek_batches('default'))
        contents = default_batch_biomek.driver_file.to_string(include_header=False)
        self.copy_to_clipboard(contents)
        self.assertEqual('target1: in-FROM:A:1,1,DNA1,5.0,0.0,1,END1,1,0', contents)
