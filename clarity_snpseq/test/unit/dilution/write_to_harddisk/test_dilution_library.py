from unittest import skip
from clarity_ext.domain.container import Container
from clarity_snpseq.test.unit.dilution.test_dilution_base import TestDilutionBase


class TestDilutionLibrary(TestDilutionBase):
    @skip('writes to harddisk')
    def test__with_three_plain_artifacts_save_to_harddisk(self):
        # Arrange
        builder = self.builder_with_lib_ext_all_files(Container.CONTAINER_TYPE_TUBE)
        # ordinary samples
        builder.add_artifact_pair(source_container_name="source1", target_container_name="tube1")
        builder.add_artifact_pair(source_container_name="source1", target_container_name="tube2")
        builder.add_artifact_pair(source_container_name="source1", target_container_name="tube3")

        # Act
        # Assert
        self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

    @skip('writes to harddisk')
    def test__with_50_plain_artifacts__save_to_harddisk(self):
        # Arrange
        builder = self.builder_with_lib_ext_all_files(Container.CONTAINER_TYPE_TUBE)
        # ordinary samples
        self._add_50_artifacts(builder)

        # Act
        # Assert
        self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

    @skip('Writes to harddisk')
    def test__with_50_artifacts_intermediate_and_evaporation__save_to_harddisk(self):
        # Arrange
        builder = self.builder_with_lib_ext_all_files(Container.CONTAINER_TYPE_TUBE)
        # ordinary samples
        self._add_50_with_evap_and_intermediate(builder)

        # Act
        # Assert
        self.save_metadata_to_harddisk(builder, r'/home/edeng655-local/smajobb/2019/mars/clarity-dilutions/dilution_files')

    def _add_50_artifacts(self, builder):
        for i in range(50):
            target_tube = 'tube{}'.format(i + 1)
            builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                      source_container_name='sourceplate1', target_container_name=target_tube)

    def _add_50_with_evap_and_intermediate(self, builder):
        for i in range(20):
            target_tube = 'tube{}'.format(i + 1)
            builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                      source_container_name='sourceplate1', target_container_name=target_tube)

        # looped sample
        builder.add_artifact_pair(source_conc=100, source_vol=40, target_conc=2, target_vol=10,
                                  source_container_name="sourceplate1", target_container_name="tube21")
        # evap sample
        builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=30, target_vol=10,
                                  source_container_name="sourceplate1", target_container_name="tube22")

        for i in range(28):
            target_tube = 'tube{}'.format(i + 23)
            builder.add_artifact_pair(source_conc=20, source_vol=40, target_conc=10, target_vol=10,
                                      source_container_name='sourceplate1', target_container_name=target_tube)
