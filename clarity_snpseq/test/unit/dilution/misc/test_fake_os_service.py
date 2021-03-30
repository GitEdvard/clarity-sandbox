
import unittest
import os
from clarity_snpseq.test.utility.helpers import FakeOsService


class TestFakeOsService(unittest.TestCase):
    def setUp(self):
        self.fake_os_service = FakeOsService()
        self.file_builder = FileBuilder(self.fake_os_service)
        self.src = r'.\src'
        self.dst = r'.\dst'
        self.fake_os_service.makedirs(self.src)
        self.fake_os_service.makedirs(self.dst)

    def test_makedirs__with_relative_path_as_input__path_exists(self):
        # Arrange
        path = r'.\dir1\dir2'

        # Act
        self.fake_os_service.makedirs(path)

        # Assert
        self.assertTrue(self.fake_os_service.exists(path))

    def test_copyfile__with_file_created_at_another_place__copy_destination_exists(self):
        # Arrange
        src = os.path.join(self.src, 'file.txt')
        dst = os.path.join(self.dst, 'file.txt')
        self.fake_os_service.filesystem.create_file(src)
        self.assertTrue(self.fake_os_service.exists(src))

        # Act
        self.fake_os_service.copy_file(src, dst)

        # Assert
        self.assertTrue(self.fake_os_service.exists(dst))

    def test_listdir__with_one_subdir_and_one_file__returns_ok(self):
        # Arrange
        dir = os.path.join(self.src, 'dir1')
        file = os.path.join(self.src, 'file.txt')
        self.fake_os_service.makedirs(dir)
        self.fake_os_service.filesystem.create_file(file)

        # Act
        res = [d for d in self.fake_os_service.listdir(self.src)]

        # Assert
        self.assertEqual(2, len(res))
        self.assertTrue('dir1' in res)
        self.assertTrue('file.txt' in res)

    def test_open_file__with_existing_file_with_contents__contents_fetched(self):
        # Arrange
        file = os.path.join(self.src, 'file.txt')
        self.fake_os_service.filesystem.create_file(file, contents='contents in file')

        # Act
        with self.fake_os_service.open_file(file, 'r') as f:
            c = f.read()

        # Assert
        self.assertEqual('contents in file', c)

    def test_open_file__with_write_text_to_file__file_contents_ok(self):
        # Arrange
        file = os.path.join(self.src, 'file.txt')
        self.fake_os_service.filesystem.create_file(file, contents='')

        # Act
        with self.fake_os_service.open_file(file, 'w') as f:
            f.write('added contents')

        # Assert
        c = self.file_builder.get_contents(file)
        self.assertEqual('added contents', c)


class FileBuilder:
    def __init__(self, fake_os_service):
        self.os_service = fake_os_service

    def get_contents(self, file_path):
        with self.os_service.open_file(file_path, 'r') as f:
            c = f.read()
        return c
