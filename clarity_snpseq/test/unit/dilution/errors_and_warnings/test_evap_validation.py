from clarity_ext import utils
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_ext_scripts.dilution.settings import TRANSFER_COMMAND_NEW_TIPS
from clarity_ext_scripts.dilution.settings import TRANSFER_COMMAND_NONE


class TestEvapTransfer(TestDilutionBase):
    def test__with_one_evap_source_has_not_enough_volume__warning(self):
        # Arrange
        builder = ExtensionBuilder.create_with_dna_extension()
        builder.add_artifact_pair(source_conc=20, source_vol=2, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        builder.extension.execute()

        # Assert
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        # messages = list(builder.extension.dilution_session.validation_service.messages)
        # print(messages[0])
        # self.assertEqual(1, 2)
        self.assertEqual(0, error_count)
        self.assertEqual(1, warning_count)
