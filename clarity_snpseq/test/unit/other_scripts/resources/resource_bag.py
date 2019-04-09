import os


def _read_contents(filename):
    here = os.path.dirname(__file__)
    path = os.path.join(here, filename)
    with open(path, 'r') as f:
        contents = f.read()
    return contents


ADAPTER_ROBOTFILE_TRUSEQ_LT = _read_contents('adapter_robotfile_truseq_lt.txt')

ADAPTER_ROBOTFILE_TRUSEQ_HT = _read_contents('adapter_robotfile_truseq_ht.txt')
