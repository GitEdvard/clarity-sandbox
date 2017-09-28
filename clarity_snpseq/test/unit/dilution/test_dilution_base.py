from __future__ import print_function
import unittest
import datetime
from clarity_ext.service.file_service import UploadFileService
from clarity_ext.service.file_service import OSService


class TestDilutionBase(unittest.TestCase):
    def save_metadata_to_harddisk(self, extension, save_directory):
        artifact_service = extension.context.artifact_service
        upload_file_service = UploadFileService(
            OSService(), artifact_service=artifact_service, disable_commits=True,
        upload_dir=save_directory)

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
        upload_file_service.upload_files(metadata_file_handle, metadata_files)
        self.assertEqual("", "Saving to harddisk makes it fail!")
