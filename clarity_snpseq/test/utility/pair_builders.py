from clarity_ext.utility.testing import DilutionTestDataHelper
from clarity_ext.domain import *
from clarity_ext.service.dilution.service import DilutionSettings
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository


class PairBuilderBase(object):
    def __init__(self, fake_artifact_repo, output_udf_dict=None):
        self.artifact_repo = fake_artifact_repo
        self.input_udf_dict = dict()
        self.output_udf_dict = output_udf_dict or dict()
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
        self.is_control = False

    def create(self):
        pair = self.artifact_repo.create_pair(pos_from=self.pos_from,
                                  pos_to=self.pos_to,
                                  source_container_name=self.source_container_name,
                                  target_container_name=self.target_container_name,
                                  source_type=self.source_type,
                                  target_type=self.target_type,
                                  source_id=self.source_id,
                                  target_id=self.target_id)
        pair.output_artifact.udf_map = UdfMapping(self.output_udf_dict)
        pair.input_artifact.udf_map = UdfMapping(self.input_udf_dict)
        if self.source_artifact_name is not None:
            pair.input_artifact.name = self.source_artifact_name
            pair.input_artifact.view_name = self.source_container_name
        if self.target_artifact_name is not None:
            pair.output_artifact.name = self.target_artifact_name
            pair.output_artifact.view_name = self.target_artifact_name
        pair.input_artifact.is_control = self.is_control
        pair.output_artifact.is_control = self.is_control
        return pair

    def with_pos_from(self, pos_from):
        self.pos_from = pos_from

    def with_pos_to(self, pos_to):
        self.pos_to = pos_to

    def with_source_container_name(self, source_container_name):
        self.source_container_name = source_container_name

    def with_target_id(self, target_id):
        self.target_id = target_id

    def with_target_container_name(self, target_container_name):
        self.target_container_name = target_container_name

    def with_source_artifact_name(self, source_name):
        self.source_artifact_name = source_name

    def with_target_artifact_name(self, target_name):
        self.target_artifact_name = target_name

    def with_output_udf(self, lims_udf_name, value):
        self.output_udf_dict[lims_udf_name] = value


class DilutionPairBuilder(PairBuilderBase):

    def __init__(self, artifact_repository):
        super(DilutionPairBuilder, self).__init__(fake_artifact_repo=artifact_repository)
        self.pair = None

    def create_pair(self, pos_from=None, pos_to=None, source_container_name=None, target_container_name=None):
        self.with_pos_from(pos_from)
        self.with_pos_to(pos_to)
        self.with_source_container_name(source_container_name)
        self.with_target_container_name(target_container_name)
        self.with_output_udf('Dil. calc target vol', None)
        self.with_output_udf('Dil. calc target conc.', None)
        self.with_output_udf('Dil. calc source vol', None)

    def with_source_concentration(self, source_conc, concentration_unit):
        #concentration_unit = DilutionSettings.concentration_unit_to_string(self.dilute_helper.concentration_unit)
        conc_source_udf = "Conc. Current ({})".format(concentration_unit)
        self.input_udf_dict[conc_source_udf] = source_conc
        self.output_udf_dict[conc_source_udf] = source_conc

    def with_source_volume(self, source_volume):
        self.input_udf_dict['Current sample volume (ul)'] = source_volume

    def with_target_concentration(self, target_conc, concentration_unit):
        #concentration_unit = DilutionSettings.concentration_unit_to_string(self.dilute_helper.concentration_unit)
        conc_target_udf = "Target conc. ({})".format(concentration_unit)
        self.output_udf_dict[conc_target_udf] = target_conc

    def with_target_volume(self, target_volume):
        self.output_udf_dict['Target vol. (ul)'] = target_volume

    def with_dilute_factor(self, dilute_factor):
        self.output_udf_dict['Dilution factor'] = dilute_factor

    def make_it_control_pair(self, control_id_prefix, control_id_index):
        self.with_source_artifact_name('Negative control')
        self.is_control = True
        self.source_id = "{}{}".format(control_id_prefix, control_id_index)
        self.with_target_artifact_name('Negative control')
