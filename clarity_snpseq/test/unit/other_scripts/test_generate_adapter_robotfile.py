import re
from unittest import skip
from clarity_ext_scripts.library_prep.generate_adapter_robotfile import Extension as AdapterExt
from clarity_ext.domain.reagent import ReagentType
from clarity_snpseq.test.utility.higher_level_builders import AdapterExtensionBuilder
from clarity_snpseq.test.unit.test_base import TestBase
from clarity_snpseq.test.unit.other_scripts.resources.resource_bag import ADAPTER_ROBOTFILE_TRUSEQ_LT
from clarity_snpseq.test.unit.other_scripts.resources.resource_bag import ADAPTER_ROBOTFILE_TRUSEQ_HT


class TestGenerateAdapterRobotfile(TestBase):
    def setup_standard(self, reagent_category):
        self.builder = AdapterExtensionBuilder()
        self.builder.create(AdapterExt)
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

    def test__with_three_analytes_TruSeq_LT__robot_file_ok(self):
        # Arrange
        self.setup_standard('TruSeq DNA LT Adapters (AD series)')
        self._create_pair('analyte1', pos_from='B:3', reagent_label='AD033')
        self._create_pair('analyte2', pos_from='A:5', reagent_label='AD055')
        self._create_pair('analyte3', pos_from='H:12', reagent_label='AD012')

        # Act
        self.builder.extension.execute()

        # Assert
        file_service = self.builder.extension.context.file_service
        contents = file_service.get_file_contents('Index driver file', 0)
        self.assertEqual(ADAPTER_ROBOTFILE_TRUSEQ_LT.split('\n'), contents.split('\r\n'))

    def test__with_TruSeqLT__name_ok(self):
        # Arrange
        self.setup_standard('TruSeq DNA LT Adapters (AD series)')
        self._create_pair('analyte1', pos_from='A:1', reagent_label='AD001')

        # Act
        self.builder.extension.execute()

        # Assert
        file_service = self.builder.extension.context.file_service
        file_name = file_service.get_file_name('Index driver file', 0)
        res = re.match('Hamilton_TruSeqLT_[0-9]{6}_IT_24-1234.txt', file_name)
        self.assertIsNotNone(res)

    def test__with_TruSeq_HT__name_ok(self):
        # Arrange
        self.setup_standard('TruSeq HT Adapters (D7-D5)')
        self._create_pair('analyte1', pos_from='A:1', reagent_label='D701-D501')

        # Act
        self.builder.extension.execute()

        # Assert
        file_service = self.builder.extension.context.file_service
        file_name = file_service.get_file_name('Index driver file', 0)
        res = re.match('Hamilton_TruSeqHT_[0-9]{6}_IT_24-1234.txt', file_name)
        self.assertIsNotNone(res)

    def test__with_three_analytes_TruSeq_HT__robot_file_ok(self):
        # Arrange
        self.setup_standard('TruSeq HT Adapters (D7-D5)')
        self._create_pair('analyte1', pos_from='B:3', reagent_label='D703-D502')
        self._create_pair('analyte2', pos_from='A:5', reagent_label='D705-D501')
        self._create_pair('analyte3', pos_from='H:12', reagent_label='D712-D508')

        # Act
        self.builder.extension.execute()

        # Assert
        file_service = self.builder.extension.context.file_service
        contents = file_service.get_file_contents('Index driver file', 0)
        self.assertEqual(ADAPTER_ROBOTFILE_TRUSEQ_HT.split('\n'), contents.split('\r\n'))
