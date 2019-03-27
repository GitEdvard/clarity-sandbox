import unittest
from unittest import skip
from clarity_ext.domain.container import Container
from clarity_ext.domain.container import PlateSize
from clarity_ext.domain.container import ContainerPosition
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestContainerSize(TestDilutionBase):
    def test_init_container__with_size_24__container_has_24_wells(self):
        # Arrange
        c = Container(size=PlateSize(height=4, width=6))
        # Act

        print(type(c.wells))

        self.print_list(c.wells, '')

        print(c.wells[(1, 1)])

        print(type(c.wells[(1, 1)]))

        # Assert
        self.assertEqual(24, len(c.wells))

    def test_container_position(self):
        container_position = ContainerPosition(1, 1)
        self.assertEqual('A:1', '{}'.format(container_position))
