import unittest
from unittest import skip
from genologics.config import USERNAME, BASEURI, PASSWORD


class TestLogin(unittest.TestCase):
    @skip
    def test_login(self):
        with open(r'C:\Smajobb\2018\Januari\clarity\Popups\tmp.txt', 'w+') as f:
            f.write('username: {}\n'.format(USERNAME))
            f.write('password: {}\n'.format(PASSWORD))
            f.write('basuri: {}\n'.format(BASEURI))

        print('username: {}'.format(USERNAME))
        print('password: {}'.format(PASSWORD))
        print('basuri: {}'.format(BASEURI))
        self.assertEqual(1, 2)