from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.pair_builders import SampleBuilder
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository
from clarity_snpseq.test.utility.misc_builders import ContextBuilder


class PreDilutionExtensionBuilder:
    def __init__(self, context_builder=None):
        artifact_repo = FakeArtifactRepository()
        self.pair_builder = PairBuilderBase(artifact_repo)
        self.context_builder = context_builder or ContextBuilder()

    def create(self, extension_type):
        builder = ExtensionBuilderFactory.create_with_base_type(
            extension_type, context_builder=self.context_builder)
        self.extension_builder = builder

    @property
    def extension(self):
        return self.extension_builder.extension

    def create_pair(self, target_artifact_id, artifact_name=None, pooling=None,
                    seq_instrument=None, number_of_lanes=None, number_samples=1,
                    conc_fc=None):
        pair_builder = self.pair_builder
        pair_builder.with_target_id(target_artifact_id)
        if artifact_name is not None:
            pair_builder.with_source_artifact_name(artifact_name)
            pair_builder.with_target_artifact_name(artifact_name)

        for i in range(number_samples):
            sample_builder = SampleBuilder()
            if pooling:
                sample_builder.with_udf('Pooling', pooling)
            sample_builder.with_udf('Sequencing instrument', seq_instrument)
            sample_builder.with_udf('Number of lanes', number_of_lanes)
            sample_builder.with_udf('conc FC', conc_fc)
            pair_builder.add_sample(sample_builder.create())
        pair_builder.with_output_udf('target_conc_nm', None)
        pair_builder.with_output_udf('target_vol_ul', None)
        pair_builder.create()
        pair = pair_builder.pair
        self.context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)
        return pair

    def create_pair_from_samples(self, target_artifact_id, artifact_name=None, samples=None):
        pair_builder = self.pair_builder
        pair_builder.with_target_id(target_artifact_id)
        if artifact_name is not None:
            pair_builder.with_source_artifact_name(artifact_name)
            pair_builder.with_target_artifact_name(artifact_name)

        for sample in samples:
            pair_builder.add_sample(sample)
        pair_builder.with_output_udf('target_conc_nm', None)
        pair_builder.with_output_udf('target_vol_ul', None)
        pair_builder.create()
        pair = pair_builder.pair
        self.context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)
        return pair


    def reset_analytes(self):
        self.context_builder.reset_analytes()

    @property
    def all_aliquot_pairs(self):
        return self.context_builder.context.artifact_service.all_aliquot_pairs()
