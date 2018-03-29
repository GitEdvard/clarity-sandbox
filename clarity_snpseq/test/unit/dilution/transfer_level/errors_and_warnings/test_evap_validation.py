from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestEvapTransfer(TestDilutionBase):
    def test__with_one_evap_source_has_not_enough_volume__warning(self):
        # Arrange
        builder = self.builder_with_dna_ext_all_files()
        builder.add_artifact_pair(source_conc=20, source_vol=2, target_conc=30, target_vol=10,
                                  source_container_name="source1", target_container_name="target1")

        # Act
        self.execute_short(builder)

        # Assert
        warning_count = builder.extension.dilution_session.validation_service.warning_count
        error_count = builder.extension.dilution_session.validation_service.error_count
        # messages = list(builder.extension.dilution_session.validation_service.messages)
        # print(messages[0])
        # self.assertEqual(1, 2)
        self.assertEqual(0, error_count)
        self.assertEqual(1, warning_count)
