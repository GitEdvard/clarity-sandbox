
import re
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

    def parse_path(self, path):
        import os
        split_path = re.split(r'[\/\\]', path)
        new_path = ''
        for part in split_path:
            new_path = os.path.join(new_path, part)
        return new_path
