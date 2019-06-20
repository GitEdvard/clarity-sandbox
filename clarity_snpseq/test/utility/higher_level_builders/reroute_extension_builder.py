import xml.etree.ElementTree as ET
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextInitializor
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository
from clarity_snpseq.test.utility.fake_collaborators import FakeSession


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
