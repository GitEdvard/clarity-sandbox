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


class AdapterExtensionBuilder:
    """
    Used to simulate an extension for generating adapter robot file
    """
    def __init__(self):
        self.context_builder = None
        self.context_initiatizer = ContextInitializor()
        self.artifact_repo = FakeArtifactRepository()
        self.extension_builder = None

    @property
    def extension(self):
        return self.extension_builder.extension

    def with_file_service_for_sensing(self):
        self.context_initiatizer.with_file_service(FileServiceForSensing())

    def with_error_warning_files(self):
        self.context_builder.with_shared_result_file(file_handle='Step log')
        self.context_builder.with_shared_result_file(file_handle='Step log')
        self.context_builder.with_shared_result_file(file_handle='Step log')
        self.context_builder.context.disable_commits = True

    def create(self, extension_type):
        fake_session = FakeSession(fake_api=FakeApiForIndexGeneration())
        self.context_initiatizer.with_session(fake_session)
        self.context_builder = ContextBuilder(context_initiator=self.context_initiatizer)
        builder = ExtensionBuilderFactory.create_with_base_type(
            extension_type, self.context_builder)
        self.extension_builder = builder

    def create_pair(self, input_artifact_name=None, pos_from=None, reagent_label=None):
        """
        :param input_artifact_name:
        :param pos_from: ContainerPosition, if left None artifact is placed in next free pos
        :return: Container and the created pair
        """
        pair_builder = PairBuilderBase(self.artifact_repo)
        pair_builder.with_source_artifact_name(input_artifact_name)
        pair_builder.with_source_container_name('inputplate1')
        pair_builder.with_source_pos(pos_from)
        pair_builder.with_reagent_label(reagent_label)
        pair_builder.create()
        container = pair_builder.artifact_repo.container_by_name('inputplate1')
        return container, pair_builder.pair


class RerouteExtensionBuilder:
    def __init__(self):
        self.extension_builder = None
        self.context_builder = None
        self.context_initiatizer = ContextInitializor()
        self.artifact_repo = FakeArtifactRepository()
        self.pair_builder = PairBuilderBase(self.artifact_repo)

    def create(self, extension_type):
        fake_session = FakeSession(fake_api=FakeApiForRerouting())
        self.context_initiatizer.with_session(fake_session)
        self.context_builder = ContextBuilder(context_initiator=self.context_initiatizer)
        builder = ExtensionBuilderFactory.create_with_base_type(
            extension_type, self.context_builder)
        self.extension_builder = builder

    def add_entry_for_available_workflows(self, entry, *search_segments):
        self.context_initiatizer.session.api.add_entry_for_available_workflows(
            entry, *search_segments)

    def add_entry_for_available_stages(self, entry, uri):
        self.context_initiatizer.session.api.add_entry_for_available_stages(entry, uri)

    @property
    def post_cache(self):
        return self.context_initiatizer.session.api.post_cache

    @property
    def extension(self):
        return self.extension_builder.extension

    def with_artifact_pair(self, input_artifact_name, pair_builder):
        pair_builder.with_source_artifact_name(input_artifact_name)
        pair_builder.with_source_id(input_artifact_name)
        pair_builder.create()
        pair = pair_builder.pair
        self.context_builder.with_analyte_pair(pair.input_artifact, pair.output_artifact)

    def with_analyte_udf(self, lims_udf_name, udf_value):
        self.pair_builder.with_output_udf(lims_udf_name, udf_value)

    def with_analyte_udf_input(self, lims_udf_name, value):
        self.pair_builder.with_input_udf(lims_udf_name, value)

    def with_analyte_attribute_input(self, name, value):
        self.pair_builder.with_attribute_input(name, value)


class FakeApiForRerouting:
    def __init__(self):
        self.xml_cache = dict()
        self.post_cache = dict()

    def add_entry_for_available_workflows(self, entry, *segments):
        uri = self.get_uri(*segments)
        if uri not in self.xml_cache:
            root = ET.Element('root')
            self.xml_cache[uri] = root
        root = self.xml_cache[uri]
        ET.SubElement(root, 'workflow', entry)

    def add_entry_for_available_stages(self, entry, uri):
        if uri not in self.xml_cache:
            root = ET.Element('root')
            self.xml_cache[uri] = root

        root = self.xml_cache[uri]
        stages = ET.SubElement(root, 'stages')
        ET.SubElement(stages, 'stage', entry)

    def get_uri(self, *segments):
        return '.'.join(segments)

    def get(self, uri):
        return self.xml_cache[uri]

    def post(self, uri, request):
        self.post_cache[uri] = request


class FakeApiForIndexGeneration:
    def __init__(self):
        self.reagent_types = list()
        self.samples = list()

    def get_reagent_types(self, name):
        return [rt for rt in self.reagent_types if rt.label == name]

    def get_samples(self, name):
        return [s for s in self.samples if s.name == name]
