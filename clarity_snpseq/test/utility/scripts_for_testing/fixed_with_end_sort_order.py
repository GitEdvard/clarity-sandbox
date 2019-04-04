from clarity_ext_scripts.dilution.base import DilutionExtension
from clarity_ext_scripts.dilution.settings.file_rendering import *
from clarity_ext_scripts.dilution.settings.single_transfer_handlers import *
from clarity_ext_scripts.dilution.settings.transfer_batch_handlers import *


class Extension(DilutionExtension):
    """
    Have a UDF for how much of the sample we should have.
    """
    def get_robot_settings(self):
        # Robot settings are defined for both known robots, but if the registered file handle
        # is not found, it's ignored when uploading the file.
        # TODO: It would make sense to query for that here, as this leads to unnecessary calculations.
        yield HamiltonRobotSettings()
        yield BiomekRobotSettings()

    def get_dilution_settings(self):
        sort_strategy = SortStrategy()
        settings = DilutionSettings(volume_calc_method=DilutionSettings.VOLUME_CALC_FIXED,
                                    fixed_sample_volume=self.context.current_step.udf_volume_in_destination_ul,
                                    concentration_ref="ng/ul",
                                    robotfile_sort_strategy=sort_strategy.output_position_sort_key)
        try:
            settings.fixed_buffer_volume = self.context.current_step.udf_volume_buffer_ul
        except AttributeError:
            settings.fixed_buffer_volume = 0
        return settings

    def get_transfer_handlers(self):
        yield FixedVolumeCalcHandler
        yield Validate

    def get_transfer_batch_handlers(self):
        yield ControlContainersShouldBeFirst
        yield HandleSlotPositioning
        yield PostProcessBatch

    def get_pairs(self):
        return [p for p in self.context.artifact_service.all_aliquot_pairs()
                if not p.input_artifact.name.lower() == "ladder"]

    def integration_tests(self):
        yield self.test("24-10162", commit=False)

