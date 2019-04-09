from __future__ import print_function
import unittest
import pyperclip


class TestBase(unittest.TestCase):
    def copy_to_clipboard(self, var):

        if isinstance(var, set):
            var = list(var)
        if isinstance(var, list):
            var = '\n\n'.join(var)
        print('copied to clipboard:\n{}'.format(var))
        pyperclip.copy('{}'.format(var))

    def print_out_dict(self, object_list, caption):
        print("{}:".format(caption))
        print("-----------------------------------------")
        for o in object_list:
            print("{}:".format(o))
            for key in o.__dict__:
                print("{} {}".format(key, o.__dict__[key]))
            print("-----------------------------------------\n")

    def print_list(self, object_list, caption):
        print("{}:".format(caption))
        print("-------------------------------------------")
        for o in object_list:
            print("{}".format(o))
        print("-------------------------------------------\n")
