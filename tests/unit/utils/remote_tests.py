from os import remove, symlink
from tempfile import mkstemp
from unittest import TestCase

from mock import MagicMock, patch

from blockwart.node import Node
from blockwart.utils import remote


class GetPathTypeTest(TestCase):
    """
    Tests blockwart.utils.remote.get_path_type.
    """
    def test_directory(self):
        node = Node(MagicMock(), "localhost")
        self.assertEqual(
            remote.get_path_type(node, "/")[0],
            'directory',
        )

    def test_doesnt_exist(self):
        _, filename = mkstemp()
        remove(filename)
        node = Node(MagicMock(), "localhost")
        self.assertEqual(
            remote.get_path_type(node, filename)[0],
            'nonexistent',
        )

    def test_file(self):
        _, filename = mkstemp()
        node = Node(MagicMock(), "localhost")
        self.assertEqual(
            remote.get_path_type(node, filename)[0],
            'file',
        )

    def test_special(self):
        node = Node(MagicMock(), "localhost")
        self.assertEqual(
            remote.get_path_type(node, "/dev/null")[0],
            'other',
        )

    def test_symlink(self):
        _, filename1 = mkstemp()
        _, filename2 = mkstemp()
        remove(filename2)
        symlink(filename1, filename2)
        node = Node(MagicMock(), "localhost")
        self.assertEqual(
            remote.get_path_type(node, filename2)[0],
            'symlink',
        )


class PathInfoTest(TestCase):
    """
    Tests blockwart.utils.remote.PathInfo.
    """
    @patch('blockwart.utils.remote.get_path_type', return_value=(
        'nonexistent', ""))
    def test_nonexistent(self, get_path_type):
        p = remote.PathInfo(MagicMock(), "/")
        self.assertFalse(p.exists)
        self.assertFalse(p.is_binary_file)
        self.assertFalse(p.is_directory)
        self.assertFalse(p.is_file)
        self.assertFalse(p.is_symlink)
        self.assertFalse(p.is_text_file)
        with self.assertRaises(ValueError):
            p.symlink_target

    @patch('blockwart.utils.remote.get_path_type', return_value=(
        'file', "data"))
    def test_binary(self, get_path_type):
        p = remote.PathInfo(MagicMock(), "/")
        self.assertTrue(p.exists)
        self.assertTrue(p.is_binary_file)
        self.assertFalse(p.is_directory)
        self.assertTrue(p.is_file)
        self.assertFalse(p.is_symlink)
        self.assertFalse(p.is_text_file)
        with self.assertRaises(ValueError):
            p.symlink_target

    @patch('blockwart.utils.remote.get_path_type', return_value=(
        'directory', "directory"))
    def test_directory(self, get_path_type):
        p = remote.PathInfo(MagicMock(), "/")
        self.assertTrue(p.exists)
        self.assertFalse(p.is_binary_file)
        self.assertTrue(p.is_directory)
        self.assertFalse(p.is_file)
        self.assertFalse(p.is_symlink)
        self.assertFalse(p.is_text_file)
        with self.assertRaises(ValueError):
            p.symlink_target

    @patch('blockwart.utils.remote.get_path_type', return_value=(
        'file', "ASCII English text"))
    def test_text(self, get_path_type):
        p = remote.PathInfo(MagicMock(), "/")
        self.assertTrue(p.exists)
        self.assertFalse(p.is_binary_file)
        self.assertFalse(p.is_directory)
        self.assertTrue(p.is_file)
        self.assertFalse(p.is_symlink)
        self.assertTrue(p.is_text_file)
        with self.assertRaises(ValueError):
            p.symlink_target

    @patch('blockwart.utils.remote.get_path_type', return_value=(
        'symlink', "symbolic link to `/47'"))
    def test_symlink(self, get_path_type):
        p = remote.PathInfo(MagicMock(), "/")
        self.assertTrue(p.exists)
        self.assertFalse(p.is_binary_file)
        self.assertFalse(p.is_directory)
        self.assertFalse(p.is_file)
        self.assertTrue(p.is_symlink)
        self.assertFalse(p.is_text_file)
        self.assertEqual(p.symlink_target, "/47")
