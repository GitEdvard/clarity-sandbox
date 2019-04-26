from abc import abstractmethod
from mock import MagicMock
from collections import namedtuple
from clarity_ext.domain import *
from clarity_ext.utils import *
from clarity_ext.service.dilution.service import DilutionSettings
from clarity_ext.service.dilution.service import SortStrategy
from clarity_ext_scripts.dilution.settings.file_rendering import MetadataInfo
from clarity_ext_scripts.dilution.settings.file_rendering import HamiltonRobotSettings
from clarity_ext_scripts.dilution.settings.file_rendering import BiomekRobotSettings
from clarity_snpseq.test.utility.helpers import StepLogService
from clarity_snpseq.test.utility.pair_builders import DilutionPairBuilder
from clarity_snpseq.test.utility.helpers import FileServiceInitializer
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.utility.context_monkey_patching import UseQcFlagPatcher
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository


class ExtensionBuilder(object):
    def __init__(self, extension_type, source_type, target_type, context_builder=None,
                 source_well_positions_from_first=True, source_plate_size=None):
        self.source_type = source_type
        self.target_type = target_type
        self.control_id_prefix = None
        self.call_index = 1
        if context_builder is None:
            context_builder = ContextBuilder()
        self.context_builder = context_builder

        self.extension = extension_type(self.context_builder.context)

        self._handle_loggers(logging.CRITICAL)
        self.well_provider = WellProvider(source_well_positions_from_first, source_plate_size)
        self.pairs = list()
        self.step_log_service = None
        self.mocked_file_service = None

    def _handle_loggers(self, logging_level):
        self.extension.logger.setLevel(logging_level)
        self.context_builder.context.dilution_service.logger.setLevel(logging_level)
        self.context_builder.context.validation_service.logger.setLevel(logging_level)

    def with_mocked_file_service(self):
        file_service_initializer = FileServiceInitializer(
            self.extension)
        self.mocked_file_service = file_service_initializer.mocked_file_service

    def with_mocked_step_log_service(self):
        # This is only one variation of mocking step logger service!
        # With many tests, this takes little bit more time
        file_service_initializer = FileServiceInitializer(
            self.extension)
        file_service_initializer.run()
        os_service = file_service_initializer.mocked_file_service.os_service
        self.step_log_service = StepLogService(self.context_builder.context, os_service)

    def with_control_id_prefix(self, prefix):
        self.control_id_prefix = prefix

    def with_evaluate_and_log_only(self):
        self.extension._queue_robot_files_for_upload = MagicMock()
        self.extension._generate_metadata_files = MagicMock(return_value=(None, None))
        self.extension._queue_metadata_files_for_upload = MagicMock()
        self.extension._queue_udf_for_update = MagicMock()

    def monkey_patch_upload_single(self):
        self.extension.context.file_service._upload_single = \
            self.mocked_file_service.mock_upload_single

    def with_mocked_use_qc_flag_from_current_state(self):
        patcher = UseQcFlagPatcher()
        self.extension.use_qc_flag_from_current_state = patcher.use_qc_flag_from_current_state

    @property
    def step_log_contents(self):
        # not working, only returns the last call
        return self.step_log_service.step_log_contents

    @property
    def step_log_calls(self):
        return self.step_log_service.step_log_calls

    def write_to_step_log_explicitly(self, text):
        self.step_log_service.write_to_step_log_explicitly(text)

    def metadata_info(self, filename, shared_robot_settings):
        return MetadataInfo(self.extension.dilution_session,
                            filename, self.extension.context.current_user,
                            self.extension.context, shared_robot_settings)

    @property
    def sorted_transfers(self):
        transfer_batches = single(
            self.extension.dilution_session.single_robot_transfer_batches_for_update())
        s = SortStrategy()
        sorted_transfers = sorted(transfer_batches.transfers, key=s.input_position_sort_key)
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

    def get_from_biomek_batches(self, batch_name):
        b = BiomekRobotSettings()
        batches = self.extension.dilution_session.transfer_batches(b.name)
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

    @property
    def context(self):
        return self.context_builder.context

    @property
    def validation_service(self):
        return self.context.validation_service

    def add_pair_from_builder(self, pair_builder):
        pair_builder.create()
        self.pairs.append(pair_builder.pair)
        self.call_index += 1
        self.context_builder.with_analyte_pair(
            pair_builder.pair.input_artifact, pair_builder.pair.output_artifact)


class DilutionExtensionBuilder(ExtensionBuilder):
    def __init__(self, extension_type, extension_initializer, context_builder=None):
        initz = extension_initializer
        super(DilutionExtensionBuilder, self).__init__(
            extension_type, initz.source_type, initz.target_type, context_builder,
            source_well_positions_from_first=initz.source_well_positions_from_first,
            source_plate_size=initz.source_container_size)
        self.artifact_repository = FakeArtifactRepository(source_container_type=initz.source_container_type,
                                                          target_container_type=initz.target_container_type)
        self.source_container_type = initz.source_container_type
        self.target_container_type = initz.target_container_type

    @abstractmethod
    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pass

    def _get_positions(self, is_control):
        well = self.well_provider.get_next_well()
        next_free_source_pos = "{}:{}".format(well.position.row_letter, well.position.col)
        if self.target_container_type == Container.CONTAINER_TYPE_96_WELLS_PLATE:
            pos_to = next_free_source_pos
        else:
            # tube
            pos_to = "A:1"

        if is_control or self.source_container_type == Container.CONTAINER_TYPE_TUBE:
            pos_from = "A:1"
        else:
            pos_from = next_free_source_pos
        return pos_from, pos_to

    def _add_artifact_pair(self, source_conc=None, source_vol=None, target_conc=None, target_vol=None,
                           dilute_factor=None,
                          source_container_name=None, target_container_name=None, is_control=False):

        pos_from, pos_to = self._get_positions(is_control)
        pair_builder = DilutionPairBuilder(self.artifact_repository)
        self._create_dilution_pair(
            pair_builder, source_conc=source_conc, source_vol=source_vol, target_conc=target_conc,
            target_vol=target_vol, dilute_factor=dilute_factor,
            source_container_name=source_container_name, target_container_name=target_container_name,
            pos_from=pos_from, pos_to=pos_to)
        if is_control:
            pair_builder.make_it_control_pair(self.control_id_prefix, self.call_index)
        pair_builder.with_target_id('target{}'.format(self.call_index))
        pair_builder.create()
        self.pairs.append(pair_builder.pair)
        self.call_index += 1
        self.context_builder.with_analyte_pair(
            pair_builder.pair.input_artifact, pair_builder.pair.output_artifact)


class ExtensionBuilderPool(DilutionExtensionBuilder):
    def __init__(self, extension_type, extension_initializer, context_builder=None):
        super(ExtensionBuilderPool, self).__init__(extension_type,
                                                   extension_initializer,
                                                   context_builder=context_builder)
        self.input_cache = list()
        self.output_cache = list()
        self.internal_index = 0

    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pair_builder.create_pair(pos_from=pos_from, pos_to=pos_to,
                         source_container_name=source_container_name,
                         target_container_name=target_container_name)

        conc_ref = self.extension.get_dilution_settings().concentration_ref
        conc_ref_str = DilutionSettings.concentration_unit_to_string(conc_ref)
        pair_builder.with_source_concentration(source_conc, conc_ref_str)
        pair_builder.with_source_volume(source_vol)
        pair_builder.with_target_concentration(target_conc, conc_ref_str)
        pair_builder.with_target_volume(target_vol)

    def add_input_artifact(self, pool_nr, conc, vol, container_name):
        args = namedtuple('input', ['pool_nr', 'conc', 'vol', 'container_name'])
        args.pool_nr = pool_nr
        args.conc = conc
        args.vol = vol
        args.container_name = container_name
        self.input_cache.append(args)
        self.internal_index += 1

    def add_pool(self, pool_nr, target_vol):
        args = namedtuple('input', ['pool_nr', 'target_vol'])
        args.pool_nr = pool_nr
        args.target_vol = target_vol
        self.output_cache.append(args)

    def assemble_pairs(self):
        for input in self.input_cache:
            output = utils.single([p for p in self.output_cache if p.pool_nr == input.pool_nr])
            self._add_artifact_pair_for_pool(input_args=input, pool_args=output)

    def _add_artifact_pair_for_pool(self, input_args, pool_args):

        pos_from, pos_to = self._get_positions(is_control=False)
        pair_builder = DilutionPairBuilder(self.artifact_repository)
        pool_name = 'Pool{}'.format(pool_args.pool_nr)
        self._create_dilution_pair(
            pair_builder, source_conc=input_args.conc, source_vol=input_args.vol,
            target_conc=input_args.conc,
            target_vol=pool_args.target_vol,
            source_container_name=input_args.container_name,
            target_container_name=pool_name,
            pos_from=pos_from, pos_to=pos_to)
        pair_builder.with_target_id(pool_name)
        pair_builder.with_target_artifact_name(pool_name)
        pair_builder.create()
        self.pairs.append(pair_builder.pair)
        self.call_index += 1
        self.context_builder.with_analyte_pair(
            pair_builder.pair.input_artifact, pair_builder.pair.output_artifact)


class ExtensionBuilderConc(DilutionExtensionBuilder):
    def __init__(self, extension_type, extension_initializer, context_builder=None):
        super(ExtensionBuilderConc, self).__init__(extension_type,
                                                   extension_initializer,
                                                   context_builder=context_builder)

    def add_artifact_pair(self, source_conc=100, source_vol=40, target_conc=10, target_vol=40,
                          source_container_name="source1", target_container_name="target1", is_control=False):
        self._add_artifact_pair(
            source_conc=source_conc, source_vol=source_vol, target_conc=target_conc,
            target_vol=target_vol, source_container_name=source_container_name,
            target_container_name=target_container_name, is_control=is_control)

    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pair_builder.create_pair(pos_from=pos_from, pos_to=pos_to,
                         source_container_name=source_container_name,
                         target_container_name=target_container_name)

        conc_ref = self.extension.get_dilution_settings().concentration_ref
        conc_ref_str = DilutionSettings.concentration_unit_to_string(conc_ref)
        pair_builder.with_source_concentration(source_conc, conc_ref_str)
        pair_builder.with_source_volume(source_vol)
        pair_builder.with_target_concentration(target_conc, conc_ref_str)
        pair_builder.with_target_volume(target_vol)


class ExtensionBuilderFixed(DilutionExtensionBuilder):
    def __init__(self, extension_type, extension_initializer, context_builder=None):
        if context_builder is None:
            context_builder = ContextBuilder()
        context_builder.with_udf_on_step("Volume in destination ul", 10)
        super(ExtensionBuilderFixed, self).__init__(extension_type,
                                                    extension_initializer,
                                                    context_builder=context_builder)

    def add_artifact_pair(self, source_vol=40, target_vol=40,
                          source_container_name="source1", target_container_name="target1", is_control=False):
        self._add_artifact_pair(
            source_vol=source_vol, target_vol=target_vol,
            source_container_name=source_container_name,
            target_container_name=target_container_name, is_control=is_control)

    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pair_builder.create_pair(pos_from=pos_from, pos_to=pos_to,
                         source_container_name=source_container_name,
                         target_container_name=target_container_name)
        pair_builder.with_source_volume(source_vol)
        pair_builder.with_target_volume(target_vol)


class ExtensionBuilderFactor(DilutionExtensionBuilder):
    def __init__(self, extension_type, extension_initializer, context_builder=None):
        super(ExtensionBuilderFactor, self).__init__(extension_type,
                                                     extension_initializer,
                                                     context_builder=context_builder)

    # Make intellisense detect the specific parameters for factor dilution,
    # ie target_conc is replaced with dilute_factor
    def add_artifact_pair(self, source_conc=None, source_vol=None, target_vol=None,
                          dilute_factor=None,source_container_name=None,
                          target_container_name=None, is_control=False):
        self._add_artifact_pair(
            source_conc=source_conc, source_vol=source_vol, dilute_factor=dilute_factor,
            target_vol=target_vol, source_container_name=source_container_name,
            target_container_name=target_container_name, is_control=is_control)

    def _create_dilution_pair(self, pair_builder, source_conc=None, source_vol=None,
                              target_conc=None, target_vol=None, dilute_factor=None,
                              source_container_name=None, target_container_name=None,
                              pos_from=None, pos_to=None):
        pair_builder.create_pair(pos_from, pos_to,
                                 source_container_name=source_container_name,
                                 target_container_name=target_container_name)
        conc_ref = self.extension.get_dilution_settings().concentration_ref
        conc_ref_str = DilutionSettings.concentration_unit_to_string(conc_ref)
        pair_builder.with_source_concentration(source_conc, conc_ref_str)
        pair_builder.with_source_volume(source_vol)
        pair_builder.with_dilute_factor(dilute_factor)
        pair_builder.with_target_volume(target_vol)


class WellProvider:
    def __init__(self, take_from_first=True, plate_size=None):
        self.plates = list()
        self.call_index = 0
        self.take_from_first = take_from_first
        self.plate_size = plate_size

    def get_next_well(self):
        if self.call_index == 0:
            index = 0
        else:
            index = self.call_index % self._number_wells
        if index == 0:
            self._add_plate()
        self.call_index += 1
        if self.take_from_first:
            well = self.plates[-1].list_wells()[index]
        else:
            well = self.plates[-1].list_wells()[-1 -index]
        return well

    def _add_plate(self):
        plate = Container(container_type=Container.CONTAINER_TYPE_96_WELLS_PLATE,
                          size=self.plate_size)
        self.plates.append(plate)

    @property
    def _number_wells(self):
        return len(self.plates[-1].list_wells())


class ExtensionInitializer:
    def __init__(self):
        self.source_type = Analyte
        self.target_type = Analyte
        self.target_container_type = Container.CONTAINER_TYPE_96_WELLS_PLATE
        self.target_container_size = None
        self.source_container_type = Container.CONTAINER_TYPE_96_WELLS_PLATE
        self.source_container_size = None
        self.source_well_positions_from_first = True

    def with_target_container_type(self, container_type):
        self.target_container_type = container_type

    def with_target_container_size(self, plate_size):
        """
        Overrides container type default size
        :param plate_size: Should be of type PlateSize(height, width)
        :return:
        """
        self.target_container_size = plate_size

    def with_source_container_size(self, plate_size):
        self.source_container_size = plate_size

    def with_source_container_type(self, container_type):
        self.source_container_type = container_type

    def with_source_well_positions_from_first(self, from_first):
        """
        Boolean, decides if source well positions starts from A:1 (first), or from
        H:12 (last) and are thereafter added in reversed order
        :param from_first: Bool
        :return:
        """
        self.source_well_positions_from_first = from_first
