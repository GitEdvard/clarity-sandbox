import unittest
from lims_snpseq.utils.flowcell_type_parser import FlowcellTypeParser


class TestParseNumberOfFlowcells(unittest.TestCase):
    def test_xp_variations(self):
        variations = [
            '1 lane/pool',
            '1 lane / pool ',
            '1lane/pool ',
            '2 lanes/pool',
            '2 lanes / pool',
            '2 lanes/ pool',
        ]
        for variation in variations:
            parser = FlowcellTypeParser(variation)
            self.assertTrue(parser.is_xp)
            self.assertTrue(parser.is_valid)
            self.assertFalse(parser.is_standard)

    def test_standard_variations(self):
        variations = [
            '1 flowcell/pool',
            '1 flowcell / pool',
            '2 flowcells/pool',
            '1 FC/pool',
            '1 FC / pool ',
        ]
        for variation in variations:
            parser = FlowcellTypeParser(variation)
            self.assertTrue(parser.is_standard, 'string: {}'.format(variation))
            self.assertTrue(parser.is_valid)
            self.assertFalse(parser.is_xp)

    def test_one_xp(self):
        var = '1 lane/pool '
        parser = FlowcellTypeParser(var)
        self.assertTrue(parser.is_xp)
        self.assertFalse(parser.is_standard)

    def test_one_standard(self):
        var = '1 flowcell / pool'
        parser = FlowcellTypeParser(var)
        self.assertTrue(parser.is_standard)
        self.assertFalse(parser.is_xp)

    def test_number_of_units(self):
        variations = [
            '1 lane/pool',
            '1 lane / pool ',
            '1lane/pool ',
            '2 lanes/pool',
            '2 lanes / pool',
            '2 lanes/ pool',
            '1 flowcell/pool',
            '1 flowcell / pool',
            '2 flowcells/pool',
            '1 FC/pool',
            '1 FC / pool ',
        ]
        for var in variations:
            parser = FlowcellTypeParser(var)
            if '1' in var:
                self.assertEqual(parser.units_per_pool, 1)
            elif '2' in var:
                self.assertEqual(parser.units_per_pool, 2)

    def test_number_of_units__with_no_number__returns_none(self):
        no_number = 'a'
        parser = FlowcellTypeParser(no_number)
        self.assertIsNone(parser.units_per_pool)
