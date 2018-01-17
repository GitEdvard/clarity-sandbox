import StringIO
from abc import abstractmethod
from clarity_ext.domain import *
from clarity_ext.utils import *
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.factor_dilution_start import Extension as ExtensionFactor
from clarity_ext_scripts.dilution.settings import MetadataInfo
from clarity_ext_scripts.dilution.settings import HamiltonRobotSettings
from clarity_snpseq.test.utility.helpers import DilutionHelpers
from clarity_snpseq.test.utility.helpers import StepLogService
from clarity_snpseq.test.utility.pair_builders import DnaPairBuilder
from clarity_snpseq.test.utility.pair_builders import FactorPairBuilder
from clarity_ext.domain.validation import ValidationException
from clarity_ext.service.file_service import FileService


class ExtensionBuilder(object):
    def __init__(self, extension_type, source_type, target_type, mock_file_service=False):
        self.source_type = source_type
        self.target_type = target_type
        self.control_id_prefix = None
        self.call_index = 1
        dilution_helper_generator = DilutionHelpers()
        self.ext_wrapper, self.dil_helper, self.mocked_file_service = \
            dilution_helper_generator.create_helpers(ext_type=extension_type,
                                                     mock_file_service=mock_file_service)
        c = Container(container_type=Container.CONTAINER_TYPE_96_WELLS_PLATE)
        self.well_list = c.list_wells()
        self.pairs = list()
        self.step_log_service = StepLogService(self, self.context_wrapper, self.mocked_file_service.os_service)

    def with_control_id_prefix(self, prefix):
        self.control_id_prefix = prefix

    def monkey_patch_upload_single(self):
        self.extension.context.file_service._upload_single = \
            self.mocked_file_service.mock_upload_single

    @property
    def step_log_contents(self):
        # not working, only returns the last call
        return  self.step_log_service.step_log_contents

    @property
    def step_log_calls(self):
        return self.step_log_service.step_log_calls

    def write_to_step_log_explicitly(self, text):
        self.step_log_service.write_to_step_log_explicitly(text)

    @property
    def extension(self):
        return self.ext_wrapper.extension

    @property
    def context_wrapper(self):
        return self.ext_wrapper.context_wrapper
    
    def metadata_info(self, filename, shared_robot_settings):
        return MetadataInfo(self.extension.dilution_session,
                            filename, self.extension.context.current_user,
                            self.extension.context, shared_robot_settings)

    @classmethod
    def create_with_dna_extension(cls, mock_file_service=False):
        return ExtensionBuilderDna(ExtensionDna, source_type=Analyte, target_type=Analyte,
                                   mock_file_service=mock_file_service)

    @classmethod
    def create_with_factor_extension(cls):
        return ExtensionBuilderFactor(ExtensionFactor, source_type=Analyte, target_type=Analyte)

    @property
    def sorted_transfers(self):
        transfer_batches = single(
            self.extension.dilution_session.single_robot_transfer_batches_for_update())
        h = HamiltonRobotSettings()
        sorted_transfers = sorted(transfer_batches.transfers, key=h.transfer_sort_key)
        return sorted_transfers

    @property
    def single_transfer(self):
        transfer_batches = single(
            self.extension.dilution_session.single_robot_transfer_batches_for_update())
        return single(transfer_batches.transfers)

    @property
    def update_queue(self):
        """
        Retrieve artifacts from context.update_queue, list them in the same order as artifacts 
         are added in this builder
        """
        update_queue = list(self.extension.context._update_queue)
        artifacts_by_id = {a.id: a for a in update_queue}
        return [artifacts_by_id[pair.output_artifact.id] for pair in self.pairs]

    def _get_from_hamilton_batches(self, batch_name):
        h = HamiltonRobotSettings()
        batches = self.extension.dilution_session.transfer_batches(h.name)
        return (b for b in batches if b.name == batch_name)

    @property
    def default_batch(self):
        return next(self._get_from_hamilton_batches("default"))

    @property
    def evap1_batch(self):
        return next(self._get_from_hamilton_batches("evaporate1"))

    @property
    def evap2_batch(self):
        return next(self._get_from_hamilton_batches("evaporate2"))

    @property
    def loop_batch(self):
        return next(self._get_from_hamilton_batches("looped"))

    @abstractmethod
    def _create_pair_builder(self):
        pass

    @abstractmethod
    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pass

    def _add_artifact_pair(self, source_conc=None, source_vol=None, target_conc=None, target_vol=None,
                           dilute_factor=None,
                          source_container_name=None, target_container_name=None, is_control=False):
        pos_from = "A:1" if is_control else None
        well = self.well_list[self.call_index - 1]
        pos_to = "{}:{}".format(well.position.row_letter, well.position.col)
        pair_builder = self._create_pair_builder()
        self._create_dilution_pair(
            pair_builder, source_conc=source_conc, source_vol=source_vol, target_conc=target_conc,
            target_vol=target_vol, dilute_factor=dilute_factor,
            source_container_name=source_container_name, target_container_name=target_container_name,
            pos_from=pos_from, pos_to=pos_to)
        if is_control:
            pair_builder.make_it_control_pair(self.control_id_prefix, self.call_index)
        pair = pair_builder.pair
        self.pairs.append(pair)
        self.call_index += 1
        self.ext_wrapper.context_wrapper.add_analyte_pair(pair.input_artifact, pair.output_artifact)


class ExtensionBuilderDna(ExtensionBuilder):
    def add_artifact_pair(self, source_conc=22.8, source_vol=38, target_conc=22, target_vol=35,
                          source_container_name="source1", target_container_name="target1", is_control=False):
        self._add_artifact_pair(
            source_conc=source_conc, source_vol=source_vol, target_conc=target_conc,
            target_vol=target_vol, source_container_name=source_container_name,
            target_container_name=target_container_name, is_control=is_control)

    def _create_pair_builder(self):
        return DnaPairBuilder(self.dil_helper)

    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pair_builder.create_dilution_pair(
            source_conc, source_vol, target_conc, target_vol, pos_from=pos_from, pos_to=pos_to,
            source_container_name=source_container_name, target_container_name=target_container_name)


class ExtensionBuilderFactor(ExtensionBuilder):
    def add_artifact_pair(self, source_conc=None, source_vol=None, target_vol=None,
                          dilute_factor=None,source_container_name=None,
                          target_container_name=None, is_control=False):
        self._add_artifact_pair(
            source_conc=source_conc, source_vol=source_vol, dilute_factor=dilute_factor,
            target_vol=target_vol, source_container_name=source_container_name,
            target_container_name=target_container_name, is_control=is_control)

    def _create_pair_builder(self):
        return FactorPairBuilder(self.dil_helper)

    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pair_builder.create_dilution_pair(
            source_conc=source_conc, source_vol=source_vol, dilute_factor=dilute_factor,
            target_vol=target_vol, source_container_name=source_container_name,
            target_container_name=target_container_name, pos_from=pos_from, pos_to=pos_to)
