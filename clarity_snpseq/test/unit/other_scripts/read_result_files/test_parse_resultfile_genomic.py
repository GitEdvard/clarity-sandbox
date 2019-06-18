import unittest
from unittest import skip
from jinja2 import Environment, PackageLoader
from clarity_snpseq.test.utility.higher_level_builders import ReadResultFileBuilder
from clarity_ext_scripts.tapestation.parse_result_file_genomic import Extension as ParseResultfileGenomic
from clarity_snpseq.test.utility.context_monkey_patching import ResultFilePatcher


class TestParseResultfileGenomic(unittest.TestCase):
    """
    This script is sorted under tapestation scripts
    """
    def setUp(self):
        builder = ReadResultFileBuilder()
        builder.with_analyte_udf('din', None)
        builder.with_analyte_udf('TS Total Conc. ng/uL', None)
        builder.with_analyte_udf('TS Range Conc. ng/uL', None)
        builder.with_analyte_udf('Peak 1 mw', None)
        builder.with_analyte_udf('TS Length (bp)', None)
        builder.with_analyte_udf('TS Observation', None)
        builder.with_analyte_udf('Dil. Calc. Source Vol.', None)
        builder.with_mocked_local_shared_file('Result XML File (required)')
        self.builder = builder

    def _create_pair(self, target_artifact_id, artifact_name=None):
        return self.builder.create_pair(target_artifact_id, artifact_name)

    def _init_builder(self, contents_as_list, container, pair):
        self.builder.create(
            ParseResultfileGenomic, contents_as_list, container, pair)

    def peaks(self, well):
        if well.artifact.name == "Ladder":
            return [{"area": 1.0}] * 14
        else:
            return [{"area": 1.0}, {"area": 4.69}, {"area": 0.03}]

    def _render_xml(self):
        self.builder.extension.peaks = self.peaks
        env = Environment(loader=PackageLoader('clarity_snpseq', 'test/unit/other_scripts/read_result_files'))
        template = env.get_template('example_tapestation_file.xml.j2')
        return template.render(ext=self.builder.extension)

    def test_render(self):
        container, pair = self._create_pair('92-998')
        self._init_builder([], container, pair)
        self._render_xml()

    def first_test(self):
        # Arrange
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder([], container, pair)
        contents = self._render_xml()
        self.builder.context_builder.with_mocked_local_shared_file(
            'Result XML File (required)', contents)
        monkey = ResultFilePatcher()
        monkey.cache['92-998'] = pair.output_artifact
        self.builder.extension.context.output_result_file_by_id = monkey.output_result_file_by_id

        # Act
        self.builder.extension.execute()

        # Assert
        #self.assertEqual(5.48, pair.output_artifact.udf_gqn)

