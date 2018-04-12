from clarity_ext.utility.testing import DilutionTestDataHelper
from clarity_ext.domain import *
from clarity_ext.service.dilution.service import DilutionSettings
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository


class DilutionPairBuilder:

    def __init__(self, dilute_helper):
        self.pair = None
        self.dilute_helper = dilute_helper

    def create_pair(self, pos_from=None, pos_to=None, source_container_name=None, target_container_name=None,
                    source_type=Analyte, target_type=Analyte):
        self.pair = self.dilute_helper.create_pair(
            pos_from=pos_from, pos_to=pos_to, source_container_name=source_container_name,
            target_container_name=target_container_name, source_type=source_type,
            target_type=target_type)
        self.pair.input_artifact.udf_map = UdfMapping()
        self.pair.output_artifact.udf_map = UdfMapping({"Dil. calc target vol": None,
                                                        "Dil. calc target conc.": None,
                                                        "Dil. calc source vol": None})

    def with_source_concentration(self, source_conc):
        concentration_unit = DilutionSettings.concentration_unit_to_string(self.dilute_helper.concentration_unit)
        conc_source_udf = "Conc. Current ({})".format(concentration_unit)
        self.pair.input_artifact.udf_map.add(conc_source_udf, source_conc)
        self.pair.output_artifact.udf_map.add(conc_source_udf, source_conc)

    def with_source_volume(self, source_volume):
        self.pair.input_artifact.udf_map.add("Current sample volume (ul)", source_volume)

    def with_target_concentration(self, target_conc):
        concentration_unit = DilutionSettings.concentration_unit_to_string(self.dilute_helper.concentration_unit)
        conc_target_udf = "Target conc. ({})".format(concentration_unit)
        self.pair.output_artifact.udf_map.add(conc_target_udf, target_conc)

    def with_target_volume(self, target_volume):
        self.pair.output_artifact.udf_map.add("Target vol. (ul)", target_volume)

    def with_dilute_factor(self, dilute_factor):
        self.pair.output_artifact.udf_map.add("Dilution factor", dilute_factor)

    def make_it_control_pair(self, control_id_prefix, control_id_index):
        self.pair.input_artifact.name = "Negative control"
        self.pair.input_artifact.view_name = "Negative control"
        self.pair.input_artifact.is_control = True
        self.pair.input_artifact.id = "{}{}".format(control_id_prefix, control_id_index)
        self.pair.output_artifact.name = "Negative control"
        self.pair.output_artifact.view_name = "Negative control"
        self.pair.output_artifact.is_control = True


class FactorPairBuilder(DilutionPairBuilder):
    def create_dilution_pair(self, source_conc, source_vol, dilute_factor, target_vol, pos_from=None, pos_to=None,
                             source_type=Analyte, target_type=Analyte,
                             source_container_name=None, target_container_name=None):
        """Creates an analyte pair ready for dilution"""
        self.create_pair(pos_from, pos_to,source_type=source_type, target_type=target_type,
                         source_container_name=source_container_name,
                         target_container_name=target_container_name)
        self.with_source_concentration(source_conc)
        self.with_source_volume(source_vol)
        self.with_dilute_factor(dilute_factor)
        self.with_target_volume(target_vol)


class DnaPairBuilder(DilutionPairBuilder):
    def create_dilution_pair(self, source_conc, source_vol, target_conc, target_vol,
                             pos_from=None, pos_to=None,
                             source_type=Analyte, target_type=Analyte,
                             source_container_name=None, target_container_name=None):
        self.create_pair(pos_from=pos_from, pos_to=pos_to,
                         source_container_name=source_container_name,
                         target_container_name=target_container_name, source_type=source_type,
                         target_type=target_type)
        self.with_source_concentration(source_conc)
        self.with_source_volume(source_vol)
        self.with_target_concentration(target_conc)
        self.with_target_volume(target_vol)


class PairBuilderBase(object):
    def __init__(self, fake_artifact_repo=None, udf_dict=None):
        self.artifact_repo = fake_artifact_repo or FakeArtifactRepository()
        self.udf_dict = udf_dict or dict()
        self.pos_from = None
        self.pos_to = None
        self.source_container_name = None
        self.target_container_name = None
        self.source_type = Analyte
        self.target_type = Analyte
        self.source_artifact_name = None
        self.target_artifact_name = None
        self.source_id = None
        self.target_id = None

    def create(self):
        pair = self.artifact_repo.create_pair(pos_from=self.pos_from,
                                  pos_to=self.pos_to,
                                  source_container_name=self.source_container_name,
                                  target_container_name=self.target_container_name,
                                  source_type=self.source_type,
                                  target_type=self.target_type,
                                  source_id=self.source_id,
                                  target_id=self.target_id)
        pair.output_artifact.udf_map = UdfMapping(self.udf_dict)
        if self.source_artifact_name is not None:
            pair.input_artifact.name = self.source_artifact_name
        if self.target_artifact_name is not None:
            pair.output_artifact.name = self.target_artifact_name
        return pair

    def with_target_id(self, target_id):
        self.target_id = target_id

    def with_target_container_name(self, target_container_name):
        self.target_container_name = target_container_name

    def with_source_artifact_name(self, source_name):
        self.source_artifact_name = source_name

    def with_target_artifact_name(self, target_name):
        self.target_artifact_name = target_name

    def with_udf(self, lims_udf_name, value):
        self.udf_dict[lims_udf_name] = value
