import os


def _read_contents(filename):
    here = os.path.dirname(__file__)
    path = os.path.join(here, filename)
    with open(path, 'r') as f:
        contents = f.read()
    return contents


ADAPTER_ROBOTFILE_TRUSEQ_LT_HAMILTON = _read_contents('adapter_robotfile_truseq_lt.txt')

ADAPTER_ROBOTFILE_TRUSEQ_HT_HAMILTON = _read_contents('adapter_robotfile_truseq_ht.txt')

ADAPTER_ROBOTFILE_TRUSEQ_LT_BIOMEK = _read_contents('adapter_robotfile_truseq_lt_biomek.txt')

ADAPTER_ROBOTFILE_TRUSEQ_HT_BIOMEK = _read_contents('adapter_robotfile_truseq_ht_biomek.txt')

ROBOTFILE_INHERENT_HAMILTON_TRUSEQ_HT = _read_contents('robotfile_inherent_hamilton_truseq_ht.txt')
