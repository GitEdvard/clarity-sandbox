from __future__ import print_function
import unittest
import re
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.pair_builders import DilutionPairBuilder
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository


class TestTransferSorting(TestDilutionBase):
    def test__init_dilution_with_sorting_strategy(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_fixed_end_sort_order()

    def test__with_sort_on_source_positions__transfers_sorted_accordingly(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_fixed_extension()
        artifact_repo = FakeArtifactRepository()
        self.add_pair(builder, artifact_repo, 'C:1', 'A:1', 'sample1')
        self.add_pair(builder, artifact_repo, 'B:1', 'B:1', 'sample2')
        self.add_pair(builder, artifact_repo, 'A:1', 'C:1', 'sample3')

        # Act
        self.execute_short(builder)

        # Assert
        sort_strategy = builder.extension.get_dilution_settings().sort_strategy
        sorted_transfers = sorted(builder.default_batch.transfers, key=sort_strategy)
        self.assertEqual(3, len(sorted_transfers))
        self.assertEqual('sample3 (source)', sorted_transfers[0].source_location.artifact.name)
        self.assertEqual('sample2 (source)', sorted_transfers[1].source_location.artifact.name)
        self.assertEqual('sample1 (source)', sorted_transfers[2].source_location.artifact.name)

    def test__with_sort_on_target_positions__transfers_sorted_accordingly(self):
        # Arrange
        builder = ExtensionBuilderFactory.create_with_fixed_end_sort_order()
        artifact_repo = FakeArtifactRepository()
        self.add_pair(builder, artifact_repo, 'C:1', 'A:1', 'sample1')
        self.add_pair(builder, artifact_repo, 'B:1', 'B:1', 'sample2')
        self.add_pair(builder, artifact_repo, 'A:1', 'C:1', 'sample3')

        # Act
        self.execute_short(builder)

        # Assert
        sort_strategy = builder.extension.get_dilution_settings().sort_strategy
        sorted_transfers = sorted(builder.default_batch.transfers, key=sort_strategy)
        self.assertEqual(3, len(sorted_transfers))
        self.assertEqual('sample1 (source)', sorted_transfers[0].source_location.artifact.name)
        self.assertEqual('sample2 (source)', sorted_transfers[1].source_location.artifact.name)
        self.assertEqual('sample3 (source)', sorted_transfers[2].source_location.artifact.name)

    def add_pair(self, builder, artifact_repo,
                 source_position,
                 target_position,
                 sample_name,
                 source_conatiner_name='source1',
                 target_container_name='target1'):
        pair_builder = DilutionPairBuilder(artifact_repo)

        pair_builder.with_pos_from(source_position)
        pair_builder.with_pos_to(target_position)
        pair_builder.with_target_container_name(target_container_name)
        pair_builder.with_source_container_name(source_conatiner_name)
        pair_builder.with_source_artifact_name('{}{}'.format(sample_name, ' (source)'))
        pair_builder.with_target_artifact_name('{}{}'.format(sample_name, ' (target)'))
        pair_builder.with_source_volume(15)
        builder.add_pair_from_builder(pair_builder)


