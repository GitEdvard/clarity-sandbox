from unittest import skip
from clarity_ext.domain.container import Container
from clarity_ext.domain.container import PlateSize
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository
from clarity_snpseq.test.utility.pair_builders import DilutionPairBuilder
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_ext.service.dilution.service import TubeRackPositioner


class TestTubeRackPositioner(TestDilutionBase):
    def setUp(self):
        self.pairs = self._create_pairs()
        self.positioner = TubeRackPositioner(PlateSize(height=4, width=6))

    def test__with_50_pairs__number_tuberacks_ok(self):
        # Arrange
        pairs = self.pairs
        positioner = self.positioner
        # Act
        self._populate_positioner(pairs, positioner)

        # Assert
        self.assertEqual(3, len(positioner.tube_racks))

    def test_convert_to_coordiantes__with_input_index_0__returns_ok(self):
        # Arrange
        positioner = self.positioner
        # Act
        row, col = positioner._convert_to_coordinates(0)

        # Assert
        self.assertEqual(0, row)
        self.assertEqual(0, col)

    def test_convert_to_coordinates__with_input_index_5__returns_ok(self):
        # Arrange
        positioner = self.positioner
        # Act
        row, col = positioner._convert_to_coordinates(5)

        # Assert
        self.assertEqual(1, row)
        self.assertEqual(1, col)

    def test_convert_to_coordinates__with_input_index_9__returns_ok(self):
        # Arrange
        positioner = self.positioner
        # Act
        row, col = positioner._convert_to_coordinates(9)

        # Assert
        self.assertEqual(1, row)
        self.assertEqual(2, col)

    def test__with_50_pairs__number_occupied_in_tube_rack1_is_24(self):
        # Arrange
        pairs = self.pairs
        positioner = self.positioner
        # Act
        self._populate_positioner(pairs, positioner)

        # Assert
        tube_rack1 = positioner.tube_racks[0]
        self.assertEqual(24, len(tube_rack1.occupied))

    def test__with_50_pairs__number_occupied_in_tube_rack3_is_2(self):
        # Arrange
        pairs = self.pairs
        positioner = self.positioner
        # Act
        self._populate_positioner(pairs, positioner)

        # Assert
        tube_rack3 = positioner.tube_racks[2]
        self.assertEqual(2, len(tube_rack3.occupied))

    def test__with_50_pairs__tube_names_at_3_locations_ok(self):
        pairs = self.pairs
        positioner = self.positioner
        # Act
        self._populate_positioner(pairs, positioner)

        # Assert
        tube_rack1 = positioner.tube_racks[0]
        tube_rack2 = positioner.tube_racks[1]
        tube_rack3 = positioner.tube_racks[2]
        c = [(tube_rack1.wells[w], tube_rack1.wells[w].artifact.container.name)
             for w in tube_rack1.wells if tube_rack1.wells[w].artifact is not None]
        # self.print_list(c, '')
        self.assertEqual('targettube6', tube_rack1.wells[(2, 2)].artifact.container.name)
        self.assertEqual('targettube32', tube_rack2.wells[(4, 2)].artifact.container.name)
        self.assertEqual('targettube50', tube_rack3.wells[(2, 1)].artifact.container.name)

    def test__with_50_pairs__get_last_populated_well_is_from_right_tuberack(self):
        pairs = self.pairs
        positioner = self.positioner
        # Act
        self._populate_positioner(pairs, positioner)

        # Assert
        self.assertEqual('Tuberack3', positioner.well_for_last_artifact.container.name)

    def test__with_50_pairs__get_last_populated_well_has_right_position(self):
        pairs = self.pairs
        positioner = self.positioner
        # Act
        self._populate_positioner(pairs, positioner)

        # Assert
        self.assertEqual('B1', '{}'.format(positioner.well_for_last_artifact.alpha_num_key))

    def _populate_positioner(self, pairs, positioner):
        for pair in pairs:
            output_artifact = pair.output_artifact
            well = output_artifact.well
            positioner.add(well)

    def _create_pairs(self):
        artifact_repo = FakeArtifactRepository(target_container_type=Container.CONTAINER_TYPE_TUBE)
        pair_builder = DilutionPairBuilder(artifact_repo)
        pairs = list()
        for i in range(50):
            row = i % 8
            col = i // 8
            pos_from = self._convert_to_position(row, col)
            pair_builder.create_pair(pos_from=pos_from, pos_to='A:1',
                                     source_container_name='source1',
                                     target_container_name='targettube{}'.format(i + 1))
            pair_builder.create()
            pairs.append(pair_builder.pair)
        return pairs

    def _convert_to_position(self, row, col):
        return '{}:{}'.format(chr(ord('A') + row), col + 1)

    def test_convert_coordinates(self):
        # zero based index
        row = 3
        col = 2
        self.assertEqual('D:3', self._convert_to_position(row, col))
