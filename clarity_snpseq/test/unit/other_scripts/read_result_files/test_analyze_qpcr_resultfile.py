import unittest
from clarity_snpseq.test.utility.higher_level_builders.read_result_file_builder import ReadResultFileBuilder
from clarity_ext_scripts.qpcr.analyze_qpcr_resultfile import Extension as AnalyzeQpcrResultfile


class TestAnalyzeQpcrResultfile(unittest.TestCase):
    def setup_standard_with_mocked_local_shared_file(self):
        self.setup_standard()
        self.builder.with_mocked_local_shared_file('Result File (.csv) (required)')
        self.builder.with_process_udf('Criteria 1 - Threshold Value', 1)
        self.builder.with_process_udf('Criteria 1 - Operator', '<')
        self.builder.with_process_udf('Criteria 1 - Source Data Field', 'xxx')

    def setup_standard(self):
        builder = ReadResultFileBuilder()
        builder.with_analyte_udf('Percentage difference', None)
        builder.with_analyte_udf('Initial qpcr conc. pm', None)
        builder.with_process_udf('qpcr kit type', 'kit type')
        builder.with_process_udf('cfx384 adjustment %', 100)
        self.builder = builder

    def _create_pair(self, target_artifact_id, artifact_name=None):
        return self.builder.create_pair(target_artifact_id, artifact_name)

    def _init_builder(self, contents_as_list, container, pair):
        self.builder.create(AnalyzeQpcrResultfile, contents_as_list, container, pair)

    def test__with_one_artifact_as_input__percentage_difference_ok(self):
        # Arrange
        self.setup_standard_with_mocked_local_shared_file()
        contents = [
            'Sample,Konc i qPCR-plattan (pM) Quantity Mean,Avvikelse',
            '92-998_Test-0003-tot1,0.68,13',
            '92-74817_Negative control,1.57,6'
        ]
        container, pair = self._create_pair('92-998')
        self._init_builder(contents, container, pair)

        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(13, pair.output_artifact.udf_percentage_difference)

    def test__with_one_artifact_as_input__udf_initial_qpcr_conc_pm_ok(self):
        # Arrange
        self.setup_standard_with_mocked_local_shared_file()
        contents = [
            'Sample,Konc i qPCR-plattan (pM) Quantity Mean,Avvikelse',
            '92-998_Test-0003-tot1,0.68,13',
            '92-74817_Negative control,1.57,6'
        ]
        container, pair = self._create_pair('92-998')
        self._init_builder(contents, container, pair)

        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(0.68, pair.output_artifact.udf_initial_qpcr_conc_pm)

    def test__with_one_artifact_as_input_and_kit_type_universal__udf_initial_qpcr_conc_pm_ok(self):
        # Arrange
        self.setup_standard_with_mocked_local_shared_file()
        self.builder.with_process_udf('qpcr kit type', 'Universal (CFX384Touch)')
        self.builder.with_process_udf('cfx384 adjustment %', 90)
        contents = [
            'Sample,Konc i qPCR-plattan (pM) Quantity Mean,Avvikelse',
            '92-998_Test-0003-tot1,0.68,13',
            '92-74817_Negative control,1.57,6'
        ]
        container, pair = self._create_pair('92-998')
        self._init_builder(contents, container, pair)

        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(1.292, pair.output_artifact.udf_initial_qpcr_conc_pm)

    def test__with_wacko_input__exception(self):
        """This test is just a current state documentation. KeyError is here not very informative at all"""
        # Arrange
        self.setup_standard_with_mocked_local_shared_file()
        contents = [
            'kkkkkkkkkkkkkkk',
            'uuuuu'
        ]
        container, pair = self._create_pair('92-998')
        self._init_builder(contents, container, pair)

        # Act
        self.assertRaises(KeyError, lambda: self.builder.extension.execute())
