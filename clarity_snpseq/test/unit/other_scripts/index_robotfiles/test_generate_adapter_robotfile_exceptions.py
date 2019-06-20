from clarity_ext_scripts.library_prep.generate_robotfile_for_indextags import Extension as AdapterExt
from clarity_ext.domain.reagent import ReagentType
from clarity_ext.domain.validation import UsageError
from clarity_snpseq.test.utility.higher_level_builders.adapter_extension_builder import AdapterExtensionBuilder
from clarity_snpseq.test.utility.fake_collaborators import FakeSample
from clarity_snpseq.test.unit.test_base import TestBase


class TestGenerateAdapterRobotfile(TestBase):
    def setup_without_sample(self, reagent_category):
        self.builder = AdapterExtensionBuilder()
        self.builder.create(AdapterExt)
        self.builder.with_error_warning_files()
        self.context_builder = self.builder.context_builder
        self.reagent_category = reagent_category

    def _create_pair(self, input_artifact_name=None, pos_from=None, reagent_label=None):
        _, pair = self.builder.create_pair(input_artifact_name, pos_from=pos_from,
                                           reagent_label=reagent_label)
        self.context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)
        if reagent_label is not None:
            self._create_reagent_type(reagent_label, self.reagent_category)

    def _create_reagent_type(self, label, category):
        reagent_type = ReagentType(label=label, category=category)
        self.context_builder.with_reagent_type(reagent_type)

    def test_with_sample_missing_for_tag_group__exception(self):
        # Arrange
        self.setup_without_sample('TruSeq DNA LT Adapters (AD series)')
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD005')

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.builder.extension.execute())

    def test__with_two_tabs_in_index_mapping_hamilton__exception(self):
        # Arrange
        self.setup_without_sample('TruSeq DNA LT Adapters (AD series)')
        sample_builder = SampleBuilder(self.context_builder, 'TruSeq_DNA_LT_Adapters_AD_series')
        sample_builder.with_lt_settings()
        sample_builder.with_index_map_hamilton(
            '\r\n'.join(['AD001\tA:1', 'AD003\t\tA:3', 'AD005\tA:5', 'AD012\tA:12']))
        sample_builder.create()
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD005')

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.builder.extension.execute())

    def test__with_two_tabs_in_index_mapping_biomek__exception(self):
        # Arrange
        self.setup_without_sample('TruSeq DNA LT Adapters (AD series)')
        sample_builder = SampleBuilder(self.context_builder, 'TruSeq_DNA_LT_Adapters_AD_series')
        sample_builder.with_lt_settings()
        sample_builder.with_index_map_biomek(
            '\r\n'.join(['AD001\tA:1', 'AD003\t\tA:3', 'AD005\tA:5', 'AD012\tA:12']))
        sample_builder.create()
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD005')

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.builder.extension.execute())

    def test__with_position_outside_dimension_in_biomek__exception(self):
        # Arrange
        self.setup_without_sample('TruSeq DNA LT Adapters (AD series)')
        sample_builder = SampleBuilder(self.context_builder, 'TruSeq_DNA_LT_Adapters_AD_series')
        sample_builder.with_lt_settings()
        sample_builder.with_index_map_biomek(
            '\r\n'.join(['AD001\tA:1', 'AD003\tA:7', 'AD005\tA:5', 'AD012\tA:12']))
        sample_builder.create()
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD005')

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.builder.extension.execute())

    def test__with_faulty_pos_format_in_index_mapping__exception(self):
        # Arrange
        self.setup_without_sample('TruSeq DNA LT Adapters (AD series)')
        sample_builder = SampleBuilder(self.context_builder, 'TruSeq_DNA_LT_Adapters_AD_series')
        sample_builder.with_lt_settings()
        sample_builder.with_index_map_hamilton(
            '\r\n'.join(['AD001\tA1', 'AD003\tA3', 'AD005\tA5', 'AD012\tA12']))
        sample_builder.create()
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD005')

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.builder.extension.execute())

    def test__with_sample_label_not_present_in_index_mapping__exception(self):
        # Arrange
        self.setup_without_sample('TruSeq DNA LT Adapters (AD series)')
        sample_builder = SampleBuilder(self.context_builder, 'TruSeq_DNA_LT_Adapters_AD_series')
        sample_builder.with_lt_settings()
        sample_builder.create()
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD111')

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.builder.extension.execute())

    def test__with_space_in_shortname__exception(self):
        # Arrange
        self.setup_without_sample('TruSeq DNA LT Adapters (AD series)')
        sample_builder = SampleBuilder(self.context_builder, 'TruSeq_DNA_LT_Adapters_AD_series')
        sample_builder.with_lt_settings()
        sample_builder.with_short_name('shortname with spaces')
        sample_builder.create()
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD005')

        # Act
        # Assert
        self.assertRaises(UsageError, lambda: self.builder.extension.execute())


class SampleBuilder:
    def __init__(self, context_builder, reagent_category):
        self.sample = FakeSample()
        self.context_builder = context_builder
        self.sample.name = 'IndexConfig_{}'.format(reagent_category)

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
            ['D701-D501\tA:1', 'D703-D502\tB:3', 'D705-D501\tA:5', 'D712-D508\tH:12'])
        self.sample.indexconfig_source_dimensions_rows_hamilton = 8
        self.sample.indexconfig_source_dimensions_columns_hamilton = 12
        self.sample.indexconfig_index_position_map_biomek = '\r\n'.join(
            ['D701-D501\tA:1', 'D703-D502\tB:3', 'D705-D501\tA:5', 'D712-D508\tH:12'])
        self.sample.indexconfig_source_dimensions_rows_biomek = 8
        self.sample.indexconfig_source_dimensions_columns_biomek = 12
        self.sample.indexconfig_short_name = 'TruSeqHT'

    def with_index_map_hamilton(self, map):
        self.sample.indexconfig_index_position_map_hamilton = map

    def with_index_map_biomek(self, map):
        self.sample.indexconfig_index_position_map_biomek = map

    def with_short_name(self, shortname):
        self.sample.indexconfig_short_name = shortname

    def create(self):
        self.context_builder.with_sample(self.sample)
