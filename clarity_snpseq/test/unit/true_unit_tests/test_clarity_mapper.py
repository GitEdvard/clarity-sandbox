import unittest
from unittest import skip
from clarity_ext.mappers.clarity_mapper import ClarityMapper
from xml.etree import ElementTree as ET


class TestClarityMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = ClarityMapper()
        self.builder = ResourceBuilder()

    def test_is_control__with_resource_having_one_sample_and_control_type_element__is_control_true(self):
        # Arrange
        self.builder.add_sample('sample1')
        self.builder.with_control_type()

        # Act
        is_control = self.mapper._is_control(self.builder.resource)

        # Assert
        self.assertTrue(is_control)

    def test_is_control__with_resource_having_one_sample_and_no_control_type__is_control_false(self):
        self.builder.add_sample('sample1')

        # Act
        is_control = self.mapper._is_control(self.builder.resource)

        # Assert
        self.assertFalse(is_control)

    def test_is_control__with_resource_having_two_samples_and_control_type_element__is_control_false(self):
        # Arrange
        self.builder.add_sample('sample1')
        self.builder.add_sample('sample2')
        self.builder.with_control_type()

        # Act
        is_control = self.mapper._is_control(self.builder.resource)

        # Assert
        self.assertFalse(is_control)


class ResourceBuilder:
    def __init__(self):
        self._root = ET.Element('root')
        self.resource = FakeApiResource()
        self.resource.root = self._root

    def add_sample(self, name):
        self.resource.samples.append(name)

    def with_control_type(self):
        ET.SubElement(self._root, 'control-type')


class FakeApiResource:
    def __init__(self):
        self.samples = list()
        self.root = None
