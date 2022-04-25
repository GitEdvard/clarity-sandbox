import unittest
import xml.etree.ElementTree as ET
from genologics.lims import Lims
from genologics.config import BASEURI, USERNAME, PASSWORD


class TestCallRest(unittest.TestCase):
    """
    Various searches on lims-prod
    """
    @unittest.skip('')
    def test_search_on_technical_first_name(self):
        api = Lims(BASEURI, USERNAME, PASSWORD)
        processes = api.get_processes(techfirstname='Edvard')
        # for p in processes:
        #     print(p.id)
        picked_process = processes[13]
        picked_process.get()
        print(picked_process.xml())
        assert False

    @unittest.skip('')
    def test_search_on_type(self):
        api = Lims(BASEURI, USERNAME, PASSWORD)
        processes = api.get_processes(type='SNP&SEQ AUTOMATED Start Illumina Sequencing (NovaSeq) v1')
        # for p in processes:
        #     print(p.id)
        picked_process = processes[0]
        picked_process.get()
        print(ET.tostring(picked_process.root))
        #print(len(processes))
        assert False

    @unittest.skip('')
    def test_search_on_udf_reminder(self):
        api = Lims(BASEURI, USERNAME, PASSWORD)
        processes = api.get_processes(
            type='SNP&SEQ Library Pooling (NovaSeq) v1',
            udf={'Reminder: Rename pools and print label': '---'}
        )
        # for p in processes:
        #     print(p.id)
        picked_process = processes[0]
        picked_process.get()
        #print(ET.tostring(picked_process.root))
        print(len(processes))
        assert False

    @unittest.skip('')
    def test_search_on_udf_kit_type_4(self):
        api = Lims(BASEURI, USERNAME, PASSWORD)
        processes = api.get_processes(
            type='SNP&SEQ Fragment DNA, Repair ends, Adenylate ends & Ligate Adapters (TruSeq Nano DNA) v2',
            udf={'Kit type 4': 'TruSeq DNA Nano LP (SP beads 24 samples) REF 15041032'}
        )
        # for p in processes:
        #     print(p.id)
        picked_process = processes[0]
        picked_process.get()
        #print(ET.tostring(picked_process.root))
        #print(len(processes))
        assert False

    @unittest.skip('')
    def test_search_on_udf_flow_cell_id(self):
        api = Lims(BASEURI, USERNAME, PASSWORD)
        processes = api.get_processes(
            type='SNP&SEQ AUTOMATED Start Illumina Sequencing (NovaSeq) v1',
            udf={'Flow Cell ID': 'HFYG5DMXX'}
        )
        # for p in processes:
        #     print(p.id)
        picked_process = processes[0]
        picked_process.get()
        print(ET.tostring(picked_process.root))
        #print(len(processes))
        assert False

    def test_search_on_udf_output_folder(self):
        api = Lims(BASEURI, USERNAME, PASSWORD)
        processes = api.get_processes(
            type='SNP&SEQ AUTOMATED Start Illumina Sequencing (NovaSeq) v1',
            udf={'Output Folder': '/mnt/seqsummaries/LIMS-integration/181003_A00181_0052_BHFYG5DMXX/'}
        )
        # for p in processes:
        #     print(p.id)
        picked_process = processes[0]
        picked_process.get()
        #print(ET.tostring(picked_process.root))
        print(len(processes))
        assert False
