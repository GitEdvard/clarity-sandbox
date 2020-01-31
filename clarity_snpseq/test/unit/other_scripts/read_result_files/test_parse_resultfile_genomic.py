import unittest
from jinja2 import Environment, PackageLoader
from clarity_snpseq.test.utility.higher_level_builders.read_result_file_builder import ReadResultFileBuilder
from clarity_ext_scripts.tapestation.parse_result_file_genomic import Extension as ParseResultfileGenomic
from clarity_ext.domain.validation import UsageError


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
        builder.with_monkey_result_file_cache()
        self.builder = builder

    def _create_pair(self, target_artifact_id, artifact_name=None):
        container, pair = self.builder.create_pair(target_artifact_id, artifact_name)
        self.builder.with_result_file('92-998', pair.output_artifact)
        return container, pair

    def _init_builder(self, container, pair):
        self.builder.create(
            ParseResultfileGenomic, [], container, pair)

    def _render_xml(self, xml_value_bag):
        env = Environment(loader=PackageLoader('clarity_snpseq', 'test/unit/other_scripts/read_result_files'))
        template = env.get_template('example_tapestation_file.xml.j2')
        return template.render(ext=self.builder.extension, xml_value_bag=xml_value_bag)

    def test__with_one_ok_sample__preset_values_from_script_found_in_udfs(self):
        # Arrange
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(container, pair)
        xml_value_bag = XmlValueBag(comment='92-998_artifact-name')
        contents = self._render_xml(xml_value_bag)
        self.builder.context_builder.with_mocked_local_shared_file(
            'Result XML File (required)', contents)

        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual(-2, pair.output_artifact.udf_dil_calc_source_vol)

    def test__with_one_ok_sample__values_from_xml_file_found_in_udfs(self):
        # Arrange
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(container, pair)
        xml_value_bag = XmlValueBag()
        xml_value_bag.comment = '92-998_artifact-name'
        xml_value_bag.observations = '\n'
        xml_value_bag.concentration = 41.5
        xml_value_bag.din = 9.4
        xml_value_bag.peaks = [Peak(size=100, quantity=0),
                               Peak(size=110, quantity=8.5)]

        contents = self._render_xml(xml_value_bag)
        self.builder.context_builder.with_mocked_local_shared_file(
            'Result XML File (required)', contents)

        # Act
        self.builder.extension.execute()

        # Assert
        self.assertEqual('(none)', pair.output_artifact.udf_ts_observation)
        self.assertEqual(41.5, pair.output_artifact.udf_ts_total_conc_ngul)
        self.assertEqual(9.4, pair.output_artifact.udf_din)
        self.assertEqual(100, pair.output_artifact.udf_peak_1_mw)
        self.assertEqual(110, pair.output_artifact.udf_ts_length_bp)
        self.assertEqual(8.5, pair.output_artifact.udf_ts_range_conc_ngul)

    def test__with_peak_size_not_present__warning(self):
        # Arrange
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(container, pair)
        self.builder.context_builder.with_shared_result_file('Step log', '1234', 'Warnings')
        xml_value_bag = XmlValueBag()
        xml_value_bag.comment = '92-998_artifact-name'
        xml_value_bag.peaks = [Peak(size=100, quantity=0),
                               Peak(size='-', quantity=8.5)]

        contents = self._render_xml(xml_value_bag)
        self.builder.context_builder.with_mocked_local_shared_file(
            'Result XML File (required)', contents)

        # Act
        self.builder.extension.execute()

        # Assert
        warning_count = self.builder.extension.context.validation_service.warning_count
        self.assertEqual(1, warning_count)

    def test__with_peak_calibrated_quantity_not_present__warning(self):
        # Arrange
        container, pair = self._create_pair(target_artifact_id='92-998')
        self._init_builder(container, pair)
        self.builder.context_builder.with_shared_result_file('Step log', '1234', 'Warnings')
        xml_value_bag = XmlValueBag()
        xml_value_bag.comment = '92-998_artifact-name'
        xml_value_bag.peaks = [Peak(size=100, quantity=0),
                               Peak(size='1', quantity='-')]

        contents = self._render_xml(xml_value_bag)
        self.builder.context_builder.with_mocked_local_shared_file(
            'Result XML File (required)', contents)

        # Act
        self.builder.extension.execute()

        # Assert
        warning_count = self.builder.extension.context.validation_service.warning_count
        self.assertEqual(1, warning_count)


class XmlValueBag:
    def __init__(self, comment=None):
        self.comment = comment
        self.observations = '\n'
        self.concentration = 0
        self.din = 0
        self.peaks = [Peak(size=0, quantity=0),
                      Peak(size=0, quantity=0)]


class Peak:
    def __init__(self, size=None, quantity=None):
        self.size = size
        self.calibrated_quantity = quantity
