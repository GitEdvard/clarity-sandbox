from __future__ import print_function
import unittest
import datetime
import pyperclip
from clarity_ext.service.file_service import FileService
from clarity_ext.service.file_service import OSService
from clarity_ext_scripts.dilution.settings.file_rendering import HamiltonRobotSettings
from clarity_ext_scripts.dilution.settings.file_rendering import BiomekRobotSettings
from clarity_ext.service.dilution.service import SortStrategy
from clarity_ext.domain.container import Container
from clarity_snpseq.test.utility.misc_builders import ContextBuilder
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder
from clarity_snpseq.test.utility.factories import ExtensionBuilderFactory


class TestDilutionBase(unittest.TestCase):
    def setUp(self):
        self.hamilton_robot_setting = HamiltonRobotSettings()
        self.biomek_robot_setting = BiomekRobotSettings()
        self.sort_strategy = SortStrategy()

    def execute_short(self, builder):
        dummy = builder.extension.dilution_session

    def builder_with_factor_ext_and_all_files(self):
        b = ContextBuilder()
        b.with_all_files()
        return ExtensionBuilderFactory.create_with_factor_extension(b)

    def builder_with_dna_ext_all_files(self):
        b = ContextBuilder()
        b.with_all_files()
        return ExtensionBuilderFactory.create_with_dna_extension(b)

    def builder_with_lib_ext_all_files(self, target_container_type=Container.CONTAINER_TYPE_96_WELLS_PLATE):
        b = ContextBuilder()
        b.with_all_files()
        return ExtensionBuilderFactory.create_with_library_dil_extension(b, target_container_type)

    def save_metadata_to_harddisk(self, builder, save_directory):
        builder.context_builder.with_all_files()
        builder.extension.execute()
        file_service = self._file_service(builder.extension, save_directory)
        # Modified code taken from DilutionSession.execute()
        today = datetime.date.today().strftime("%y%m%d")
        metadata_file_handle = "Metadata"
        metadata_files = list()
        dilution_session = builder.extension.dilution_session
        print("Saving files to harddisk in folder {}".format(save_directory))
        try:
            for robot in dilution_session.robot_settings:
                metadata_file_name = "{}_{}_{}_{}.xml".format(robot.name, today, "EE", "1234")
                metadata_files.append((metadata_file_name,
                                       builder.extension.generate_metadata_file(robot, metadata_file_name)))
                print("file: {}".format(metadata_file_name))
        except:
            raise Exception('Could not export to hard disk. Preparation to export to harddisk:\n'
                            '1) call builder.extension.execute() instead of self.execute_short(builder)\n'
                            '2) File handles must be initialized in ExtensionBuilder, \n'
                            'context_builder = ContextBuilder()\n'
                            'context_builder.with_all_files()\n'
                            'builder = ExtensionBuilder.create_with_dna_extension(context_builder=context_builder)')

        # Upload the metadata file:
        file_service.upload_files(metadata_file_handle, metadata_files)
        self.assertEqual("", "Saving to harddisk makes it fail!")

    def save_robot_files_to_harddisk(self, builder, save_directory):
        builder.context_builder.with_all_files()
        upload_file_service = self._file_service(builder.extension, save_directory)
        dilution_session = builder.extension.dilution_session
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

    def copy_to_clipboard(self, var):

        if isinstance(var, set):
            var = list(var)
        if isinstance(var, list):
            var = '\n\n'.join(var)
        print('copied to clipboard:\n{}'.format(var))
        pyperclip.copy('{}'.format(var))

    def _file_service(self, extension, save_directory):
        artifact_service = extension.context.artifact_service
        file_service = FileService(artifact_service=artifact_service,
                                   file_repo=None, should_cache=False, os_service=OSService(),
                                   uploaded_to_stdout=False, disable_commits=True)
        file_service.temp_path = save_directory
        return file_service

    def print_out_dict(self, object_list, caption):
        print("{}:".format(caption))
        print("-----------------------------------------")
        for o in object_list:
            print("{}:".format(o))
            for key in o.__dict__:
                print("{} {}".format(key, o.__dict__[key]))
            print("-----------------------------------------\n")

    def print_list(self, object_list, caption):
        print("{}:".format(caption))
        print("-------------------------------------------")
        for o in object_list:
            print("{}".format(o))
        print("-------------------------------------------\n")
