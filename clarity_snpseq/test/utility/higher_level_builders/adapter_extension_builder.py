from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory
from clarity_snpseq.test.utility.misc_builders import ContextInitializor
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository
from clarity_snpseq.test.utility.helpers import FileServiceForSensing
from clarity_snpseq.test.utility.fake_collaborators import FakeSession


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


class FakeApiForIndexGeneration:
    def __init__(self):
        self.reagent_types = list()
        self.samples = list()

    def get_reagent_types(self, name):
        return [rt for rt in self.reagent_types if rt.label == name]

    def get_samples(self, name):
        return [s for s in self.samples if s.name == name]


class FakeSample:
    def __init__(self):
        self.name = None
        self.project = None
        self.id = None
        self.indexconfig_index_position_map_hamilton = None
        self.indexconfig_source_dimensions_columns_hamilton = None
        self.indexconfig_source_dimensions_rows_hamilton = None
        self.indexconfig_index_position_map_biomek = None
        self.indexconfig_source_dimensions_columns_biomek = None
        self.indexconfig_source_dimensions_rows_biomek = None
        self.indexconfig_short_name = None

    @property
    def udf(self):
        return self.__dict__
