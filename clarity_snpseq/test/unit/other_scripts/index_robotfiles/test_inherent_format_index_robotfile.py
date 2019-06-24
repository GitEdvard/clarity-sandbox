import re
from clarity_ext_scripts.library_prep.generate_converted_robotfile_for_hamilton_indextags import Extension as AdapterExt
from clarity_ext.domain.reagent import ReagentType
from clarity_snpseq.test.utility.higher_level_builders.adapter_extension_builder import AdapterExtensionBuilder
from clarity_snpseq.test.utility.fake_collaborators import FakeSample
from clarity_snpseq.test.unit.test_base import TestBase
from clarity_snpseq.test.unit.other_scripts.index_robotfiles.resources.resource_bag import ROBOTFILE_INHERENT_HAMILTON_TRUSEQ_HT


class TestInherentFormatIndexRobotfile(TestBase):
    def setup_standard(self, reagent_category):
        self.builder = AdapterExtensionBuilder()
        self.builder.with_file_service_for_sensing()
        self.builder.create(AdapterExt)
        self.context_builder = self.builder.context_builder
        self.reagent_category = reagent_category
        self._create_sample(reagent_category)

    def _create_pair(self, input_artifact_name=None, pos_from=None, reagent_label=None):
        _, pair = self.builder.create_pair(input_artifact_name, pos_from=pos_from,
                                           reagent_label=reagent_label)
        self.context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)
        if reagent_label is not None:
            self._create_reagent_type(reagent_label, self.reagent_category)

    def _create_reagent_type(self, label, category):
        reagent_type = ReagentType(label=label, category=category)
        self.context_builder.with_reagent_type(reagent_type)

    def _create_sample(self, reagent_category):
        sample_builder = SampleBuilder(self.context_builder, reagent_category)
        if reagent_category == 'TruSeq DNA LT Adapters (AD series)':
            sample_builder.with_lt_settings()
        else:
            sample_builder.with_ht_settings()
        sample_builder.create()

    def test__with_TruSeq_HT__hamilton_name_ok(self):
        # Arrange
        self.setup_standard('TruSeq HT Adapters (D7-D5)')
        self._create_pair('analyte1', pos_from='A:1', reagent_label='D701-D501 (AAA)')

        # Act
        self.builder.extension.execute()

        # Assert
        file_service = self.builder.extension.context.file_service
        file_name = file_service.get_file_name('HAM driver file', 0)
        res = re.match('Hamilton_TruSeqHT_[0-9]{6}_IT_24-1234.txt', file_name)
        self.assertIsNotNone(res)

    def test__with_three_analytes_TruSeq_HT__hamilton_robot_file_ok(self):
        # Arrange
        self.setup_standard('TruSeq HT Adapters (D7-D5)')
        self._create_pair('analyte2', pos_from='A:5', reagent_label='D703-D502 (AAA)')
        self._create_pair('analyte1', pos_from='B:3', reagent_label='D705-D501 (AAA)')
        self._create_pair('analyte3', pos_from='H:12', reagent_label='D712-D508 (AAA)')

        # Act
        self.builder.extension.execute()

        # Assert
        file_service = self.builder.extension.context.file_service
        contents = file_service.get_file_contents('HAM driver file', 0)
        expected = ROBOTFILE_INHERENT_HAMILTON_TRUSEQ_HT.split('\n')
        # remove line containing todays date
        del expected[1]
        contents = contents.split('\r\n')
        del contents[1]
        self.assertEqual(expected, contents)


class SampleBuilder:
    def __init__(self, context_builder, reagent_category):
        self.sample = FakeSample()
        self.context_builder = context_builder
        adjusted_category = reagent_category.replace(' ', '_')
        adjusted_category = re.sub('\W+', '', adjusted_category)
        self.sample.name = 'IndexConfig_{}'.format(adjusted_category)

    def with_lt_settings(self):
        self.sample.indexconfig_index_position_map_hamilton = '\r\n'.join(
            ['AD001\tA:1', 'AD003\tA:3', 'AD005\tA:5', 'AD012\tA:12'])
        self.sample.indexconfig_source_dimensions_rows_hamilton = 1
        self.sample.indexconfig_source_dimensions_columns_hamilton = 32
        self.sample.indexconfig_index_position_map_biomek = '\r\n'.join(
            ['AD001\tA:1', 'AD003\tC:1', 'AD005\tA:2', 'AD012\tD:3'])
        self.sample.indexconfig_source_dimensions_rows_biomek = 4
        self.sample.indexconfig_source_dimensions_columns_biomek = 6
        self.sample.indexconfig_short_name = 'TruSeqLT'

    def with_ht_settings(self):
        self.sample.indexconfig_index_position_map_hamilton = '\r\n'.join(
            ['D701-D501 (AAA)\tA:1', 'D703-D502 (AAA)\tB:3', 'D705-D501 (AAA)\tA:5', 'D712-D508 (AAA)\tH:12'])
        self.sample.indexconfig_source_dimensions_rows_hamilton = 8
        self.sample.indexconfig_source_dimensions_columns_hamilton = 12
        self.sample.indexconfig_index_position_map_biomek = '\r\n'.join(
            ['D701-D501 (AAA)\tA:1', 'D703-D502 (AAA)\tB:3', 'D705-D501 (AAA)\tA:5', 'D712-D508 (AAA)\tH:12'])
        self.sample.indexconfig_source_dimensions_rows_biomek = 8
        self.sample.indexconfig_source_dimensions_columns_biomek = 12
        self.sample.indexconfig_short_name = 'TruSeqHT'

    def with_index_map_hamilton(self, map):
        self.sample.indexconfig_index_position_map_hamilton = map

    def with_short_name(self, shortname):
        self.sample.indexconfig_short_name = shortname

    def create(self):
        self.context_builder.with_sample(self.sample)
