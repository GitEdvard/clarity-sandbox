from __future__ import print_function
import unittest
import datetime
from clarity_ext.service.file_service import FileService
from clarity_ext.service.file_service import OSService
from clarity_ext_scripts.dilution.settings import HamiltonRobotSettings
from clarity_ext_scripts.dilution.settings import BiomekRobotSettings


class TestDilutionBase(unittest.TestCase):
    def setUp(self):
        self.hamilton_robot_setting = HamiltonRobotSettings()
        self.biomek_robot_setting = BiomekRobotSettings()

    def save_metadata_to_harddisk(self, extension, save_directory):
        file_service = self._file_service(extension, save_directory)
        # Modified code taken from DilutionSession.execute()
        today = datetime.date.today().strftime("%y%m%d")
        metadata_file_handle = "Metadata"
        metadata_files = list()
        dilution_session = extension.dilution_session
        print("Saving files to harddisk in folder {}".format(save_directory))
        for robot in dilution_session.robot_settings:
            metadata_file_name = "{}_{}_{}_{}.xml".format(robot.name, today, "EE", "1234")
            metadata_files.append((metadata_file_name, extension.generate_metadata_file(robot, metadata_file_name)))
            print("file: {}".format(metadata_file_name))

        # Upload the metadata file:
        file_service.upload_files(metadata_file_handle, metadata_files)
        self.assertEqual("", "Saving to harddisk makes it fail!")

    def save_robot_files_to_harddisk(self, extension, save_directory):
        upload_file_service = self._file_service(extension, save_directory)
        dilution_session = extension.dilution_session
        print("Saving files to harddisk in folder {}".format(save_directory))

        robot_files_by_type = dict()
        for robot in dilution_session.robot_settings:
            files = dilution_session.transfer_batches_by_robot[robot.name].driver_files
            for ftype, f in files.items():
                robot_files_by_type.setdefault(ftype, list())
                robot_files_by_type[ftype].append(f)
        map_batch_to_file_handle = \
            {
                "default": "Final",
                "evaporate1": "Evaporate step 1",
                "evaporate2": "Evaporate step 2",
                "looped": "Intermediate"
            }
        for ftype, files in robot_files_by_type.items():
            print("-"*40)
            for f in files:
                print(f.to_string(include_header=False))
            files_with_name = [(f.file_name, f.to_string(include_header=False)) for f in files]
            file_handle = map_batch_to_file_handle[ftype]
            upload_file_service.upload_files(file_handle, files_with_name)
        self.assertEqual("", "Saving to harddisk makes it fail!")

    def _file_service(self, extension, save_directory):
        artifact_service = extension.context.artifact_service
        file_service = FileService(artifact_service=artifact_service,
                                   file_repo=None, should_cache=False, os_service=OSService(),
                                   uploaded_to_stdout=False, disable_commits=True)
        file_service.temp_path = save_directory
        return file_service
