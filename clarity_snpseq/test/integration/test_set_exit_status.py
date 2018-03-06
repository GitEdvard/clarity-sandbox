import unittest
import pyperclip
from clarity_snpseq.test.misc.from_stockholm.setExitStatus import main


class TestSetExitStatus(unittest.TestCase):
    def test_write_out_xml_for_set_exit_status(self):
        new_xml, XML, response = main()
        print(new_xml)
        pyperclip.copy(response)
        self.assertEqual(1, 2)