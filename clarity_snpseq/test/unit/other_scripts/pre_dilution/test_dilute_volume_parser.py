import unittest
import os
import yaml
import clarity_ext_scripts.dilution.settings
from clarity_ext_scripts.dilution.settings.lib_target_volume_parser import LibTargetVolumeParser


class TestDiluteVolumeParser(unittest.TestCase):
    def setUp(self):
        config, name = self._read_config()
        self.volume_parser = LibTargetVolumeParser(config=config, config_file_name=name)

    def _read_config(self):
        dir_name = os.path.dirname(clarity_ext_scripts.dilution.settings.__file__)
        config_file_name = 'dilute_volumes_before_pooling.yaml'
        path = os.path.join(dir_name, config_file_name)
        with open(path, 'r') as f:
            config = yaml.load(f)
        return config, config_file_name

    def _read_tailored_config(self, name):
        here = os.path.dirname(__file__)
        path = os.path.join(here, name)
        with open(path, 'r') as f:
            config = yaml.load(f)

        return config, name

    def test_no_match_returns_none(self):
        volume = self.volume_parser.get_from(libraries_per_pool=1, instrument='xxx', units_per_pool=1)
        self.assertIsNone(volume)

    def test__with_miseq__returns_14(self):
        volume = self.volume_parser.get_from(libraries_per_pool=1, instrument='miseq', units_per_pool=1)
        self.assertEqual(14, volume)

    def test__with_config_missing_target_volume__exception(self):
        config, name = self._read_tailored_config('config_missing_target_volume.yaml')
        parser = LibTargetVolumeParser(config=config, config_file_name=name)
        with self.assertRaises(ImportError):
            parser.get_from(libraries_per_pool=1, instrument='some instrument', units_per_pool=1)

    def test__with_novaseq_standard_s1__returns_140(self):
        volume = self.volume_parser.get_from(
            libraries_per_pool=1, instrument='novaseq', novaseq_run_type='standard',
            flowcell_type='S1', units_per_pool=1)
        self.assertEqual(140, volume)

    def test__with_novaseq_xp_s1__returns_30(self):
        volume = self.volume_parser.get_from(
            libraries_per_pool=1, instrument='novaseq', novaseq_run_type='xp',
            flowcell_type='S1', units_per_pool=1)
        self.assertEqual(30, volume)

    def test__with_miseq_2_lib_per_pool__returns_7(self):
        volume = self.volume_parser.get_from(libraries_per_pool=2, instrument='miseq', units_per_pool=1)
        self.assertEqual(7, volume)

    def test__with_novaseq_xp_s1_and_lane_per_pool_is_2__returns_60(self):
        volume = self.volume_parser.get_from(
            libraries_per_pool=1, instrument='novaseq', novaseq_run_type='xp', flowcell_type='s1',
            units_per_pool=2
        )
        self.assertEqual(60, volume)
