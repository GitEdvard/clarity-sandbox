import unittest
from unittest import skip
from clarity_ext.service.dilution.service import SortStrategy
import re


class TestPlateSortOrder(unittest.TestCase):
    def create_container(self, name, is_temporary):
        c = Dummy()
        c.name = name
        c.is_temporary = is_temporary
        c.sort_weight = 0
        return c

    @property
    def sort_key(self):
        return SortStrategy.container_sort_key

    skip('')
    def test__with_plate_name_text_first_number_last__sort_tuple_ok(self):
        platename = "code-123_Plate432_org_171010"
        c = self.create_container(platename, False)
        sortlist = self.sort_key(c)
        print(sortlist)
        self.assertEqual((0, True, 'code', 123, 'plate', 432, 'org', 171010), sortlist)

    @skip('')
    def test__with_plate_name_text_first_text_last__sort_tuple_ok(self):
        platename = "code-123_Plate432_org"
        c = self.create_container(platename, False)
        sortlist = self.sort_key(c)
        print(sortlist)
        self.assertEqual((0, True, 'code', 123, 'plate', 432, 'org', 0), sortlist)

    @skip('')
    def test_split(self):
        mystr = 'hej'
        mysplit = re.split('\D+', mystr)
        print(mysplit)
        self.assertFalse(True)

    def test_create_sort_key__single_string(self):
        platename = 'hej'
        key = SortStrategy.create_sort_key_from(platename)
        self.assertEqual(key, ['hej', 0])

    def test_sort_key__single_number(self):
        platename = '1234'
        key = SortStrategy.create_sort_key_from(platename)
        self.assertEqual(key, ['', 1234])

    def test_sort_key__two_numbers_in_part(self):
        platename = '1name234'
        key = SortStrategy.create_sort_key_from(platename)
        self.assertEqual(key, ['name', 1, '', 234])

    def test_sort_key__two_strings_in_part(self):
        platename = 'hel56lo'
        key = SortStrategy.create_sort_key_from(platename)
        self.assertEqual(key, ['hel', 56, 'lo', 0])

    def test_sort_key__two_parts(self):
        platename = 'ab1-sample2'
        key = SortStrategy.create_sort_key_from(platename)
        self.assertEqual(key, ['ab', 1, 'sample', 2])

    def test_sort_key__decimal_point(self):
        platename = '123.456'
        key = SortStrategy.create_sort_key_from(platename)
        self.assertEqual(key, ['.', 123, '', 456])


class Dummy:
    pass
