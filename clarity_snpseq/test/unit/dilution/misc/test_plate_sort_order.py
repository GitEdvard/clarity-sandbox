
import unittest
from clarity_ext.service.dilution.service import SortStrategy


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

    def test__with_plate_name_text_first_number_last__sort_tuple_ok(self):
        platename = "code-123_Plate432_org_171010"
        c = self.create_container(platename, False)
        sortlist = self.sort_key(c)
        print(sortlist)
        self.assertEqual((0, True, 'code', 0, '', 123, 'plate', 432, 'org', 0, '', 171010), sortlist)

    def test__with_plate_name_text_first_text_last__sort_tuple_ok(self):
        platename = "code-123_Plate432_org"
        c = self.create_container(platename, False)
        sortlist = self.sort_key(c)
        print(sortlist)
        self.assertEqual((0, True, 'code', 0, '', 123, 'plate', 432, 'org', 0), sortlist)

    def test__with_only_text__sort_tuple_ok(self):
        s = "text"
        c = self.create_container(s, False)
        sortlist = self.sort_key(c)
        self.assertEqual((0, True,  'text', 0), sortlist)

    def test_with_empty_string__sort_tuple_ok(self):
        s = ''
        c = self.create_container(s, False)
        sortlist = self.sort_key(c)
        self.assertEqual((0, True), sortlist)

    def test__with_only_number__sort_tuple_ok(self):
        s = "123"
        c = self.create_container(s, False)
        sortlist = self.sort_key(c)
        self.assertEqual((0, True, '', 123), sortlist)

    def test__with_plate_name_number_first_number_last__sort_tuple_ok(self):
        platename = "123-codE_321_plate1_lib_171013"
        c = self.create_container(platename, False)
        sortlist = self.sort_key(c)
        self.assertEqual((0, True, '', 123, 'code', 0, '', 321, 'plate', 1, 'lib', 0, '', 171013), sortlist)

    def test__with_plate_name_number_first_text_last__sort_tuple_ok(self):
        platename = "123-codE_321_plate1_lib"
        c = self.create_container(platename, False)
        sortlist = self.sort_key(c)
        self.assertEqual((0, True, '', 123, 'code', 0, '', 321, 'plate', 1, 'lib', 0), sortlist)

    def test__with_two_plates__sorting_with_tuples_work(self):
        name1 = "code-129"
        name2 = "code-1210"
        plate1 = self.create_container(name1, False)
        plate2 = self.create_container(name2, False)
        platelist = sorted([plate2, plate1], key=self.sort_key)
        self.assertEqual("code-129", platelist[0].name)
        self.assertEqual("code-1210", platelist[1].name)

    def test__with_two_plates_with_string_only_names__sorting_ok(self):
        name1 = "plateone"
        name2 = "platetwo"
        plate1 = self.create_container(name1, False)
        plate2 = self.create_container(name2, False)
        platelist = sorted([plate2, plate1], key=self.sort_key)
        self.assertEqual("plateone", platelist[0].name)
        self.assertEqual("platetwo", platelist[1].name)

    def test__with_two_plates_different_name_types__sorting_ok(self):
        name1 = "plate_123"
        name2 = "plateone"
        plate1 = self.create_container(name1, False)
        plate2 = self.create_container(name2, False)
        platelist = sorted([plate2, plate1], key=self.sort_key)
        self.assertEqual("plate_123", platelist[0].name)
        self.assertEqual("plateone", platelist[1].name)

    def test_validation_error__with_one_lims_id_and_one_ordinary_name(self):
        name1 = "27-8473"
        name2 = "Test-RNA1_PL1_org_210428"
        plate1 = self.create_container(name1, False)
        plate2 = self.create_container(name2, False)
        platelist = sorted([plate2, plate1], key=self.sort_key)
        self.assertEqual("27-8473", platelist[0].name)
        self.assertEqual("Test-RNA1_PL1_org_210428", platelist[1].name)

    def test__with_one_temp_plate__sorting_ok(self):
        name1 = "plate_1"
        name2 = "plate_2"
        plate1 = self.create_container(name1, False)
        plate2 = self.create_container(name2, is_temporary=True)
        platelist = sorted([plate2, plate1], key=self.sort_key)
        self.assertEqual("plate_2", platelist[0].name)
        self.assertEqual("plate_1", platelist[1].name)


class Dummy():
    pass