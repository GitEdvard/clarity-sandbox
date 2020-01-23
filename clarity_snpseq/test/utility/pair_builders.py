from clarity_ext.domain import *
from clarity_ext.domain.aliquot import Sample
from clarity_ext.domain.udf import UdfMapping


class PairBuilderBase(object):
    def __init__(self, fake_artifact_repo, output_udf_dict=None):
        self.artifact_repo = fake_artifact_repo
        self.input_udf_dict = dict()
        self.output_udf_dict = output_udf_dict or dict()
        self.input_attribute_dict = dict()
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
        self.is_control_pair = False
        self.is_source_control = False
        self.reagent_labels = list()
        self.pair = None
        self.samples = list()

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
        pair.input_artifact.reagent_labels = self.reagent_labels
        pair.input_artifact.is_control = self.is_control_pair
        pair.output_artifact.is_control = self.is_control_pair
        if self.is_source_control:
            pair.input_artifact.is_control = True
        for key in self.input_attribute_dict:
            setattr(pair.input_artifact, key, self.input_attribute_dict[key])
        if len(self.samples) > 0:
            pair.input_artifact.samples = self.samples
            pair.output_artifact.samples = self.samples
        self.pair = pair

    def add_sample(self, sample):
        self.samples.append(sample)

    def with_source_pos(self, pos_from):
        self.pos_from = pos_from

    def with_target_pos(self, pos_to):
        self.pos_to = pos_to

    def with_source_container_name(self, source_container_name):
        self.source_container_name = source_container_name

    def with_target_id(self, target_id):
        self.target_id = target_id

    def with_source_id(self, source_id):
        self.source_id = source_id

    def with_target_container_name(self, target_container_name):
        self.target_container_name = target_container_name

    def with_source_artifact_name(self, source_name):
        self.source_artifact_name = source_name

    def with_target_artifact_name(self, target_name):
        self.target_artifact_name = target_name

    def with_reagent_label(self, label):
        self.reagent_labels.append(label)

    def with_output_udf(self, lims_udf_name, value):
        self.output_udf_dict[lims_udf_name] = value

    def with_input_udf(self, lims_udf_name, value):
        self.input_udf_dict[lims_udf_name] = value

    def with_attribute_input(self, attribute_name, value):
        self.input_attribute_dict[attribute_name] = value


class DilutionPairBuilder(PairBuilderBase):

    def __init__(self, artifact_repository):
        super(DilutionPairBuilder, self).__init__(fake_artifact_repo=artifact_repository)

    def create_pair(self, pos_from=None, pos_to=None, source_container_name=None, target_container_name=None):
        self.with_source_pos(pos_from)
        self.with_target_pos(pos_to)
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
        self.is_control_pair = True
        self.source_id = "{}{}".format(control_id_prefix, control_id_index)
        self.with_target_artifact_name('Negative control')


class SampleBuilder:
    def __init__(self):
        self.udf_dict = dict()
        self.name = None
        self.sample_id = None

    def with_udf(self, udf_name, value):
        self.udf_dict[udf_name] = value

    def create(self):
        mapping = UdfMapping(self.udf_dict)
        s = Sample(self.sample_id, self.name, None, udf_map=mapping)
        return s
