import xml.etree.ElementTree as ET
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import FakeStepRepoBuilder
from clarity_snpseq.test.utility.misc_builders import ContextInitializor
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository
from clarity_snpseq.test.utility.helpers import FileServiceForSensing
from clarity_snpseq.test.utility.fake_collaborators import FakeSession


class ReadResultFileBuilder:
    """
    So far used for Analyze qpcr resultfile and
    analyze quality table
    """
    def __init__(self):
        self.shared_file_handle = None
        self.context_builder = None
        self.step_repo_builder = FakeStepRepoBuilder()
        artifact_repo = FakeArtifactRepository()
        self.pair_builder = PairBuilderBase(artifact_repo)
        self.extension_builder = None

    def create_pair(self, target_artifact_id, artifact_name=None):
        artifact_pair_builder = self.pair_builder
        artifact_pair_builder.with_target_id(target_artifact_id)
        artifact_pair_builder.with_target_container_name('target')
        if artifact_name is not None:
            artifact_pair_builder.with_source_artifact_name(artifact_name)
            artifact_pair_builder.with_target_artifact_name(artifact_name)
        container = artifact_pair_builder.artifact_repo.container_by_name('target')
        artifact_pair_builder.create()
        return container, artifact_pair_builder.pair

    @property
    def extension(self):
        return self.extension_builder.extension

    def create(self, extension_type, contents_as_list, container, pair):
        context_initiator = ContextInitializor(self.step_repo_builder)
        self.context_builder = ContextBuilder(context_initiator)
        self._configure_context_builder(contents_as_list, container, pair)
        builder = ExtensionBuilderFactory.create_with_base_type(
            extension_type, self.context_builder)
        builder.with_mocked_use_qc_flag_from_current_state()
        self.extension_builder = builder

    def _configure_context_builder(self, contents_as_list, container, pair):
        contents = '\n'.join(contents_as_list)
        self.context_builder.with_mocked_local_shared_file(self.shared_file_handle,
                                                      contents)
        self.context_builder.with_output_container(container=container)
        self.context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)

    def with_analyte_udf(self, lims_udf_name, udf_value):
        self.pair_builder.with_output_udf(lims_udf_name, udf_value)

    def with_process_udf(self, lims_udf_name, udf_value):
        self.step_repo_builder.with_process_udf(lims_udf_name, udf_value)

    def with_mocked_local_shared_file(self, filehandle):
        self.shared_file_handle = filehandle

    def with_shared_result_file(self, file_handle, with_id=None, existing_file_name=None,
                                existing_contents=None):
        self.context_builder.with_shared_result_file(file_handle, with_id, existing_file_name,
                                                           existing_contents)
