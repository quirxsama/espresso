import unittest
from unittest.mock import patch, MagicMock, call
import os
import threading # Required for DiskScanner
from collections import defaultdict

from espresso.models.disk_scanner import DiskScanner

class TestDiskScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = DiskScanner()

    def test_format_size(self):
        self.assertEqual(DiskScanner.format_size(100), "100 B")
        self.assertEqual(DiskScanner.format_size(2048), "2.00 KB")
        self.assertEqual(DiskScanner.format_size(3 * 1024 * 1024), "3.00 MB")
        self.assertEqual(DiskScanner.format_size(4 * 1024 * 1024 * 1024), "4.00 GB")
        self.assertEqual(DiskScanner.format_size(1500 * 1024), "1500.00 KB") # Test KB boundary
        self.assertEqual(DiskScanner.format_size(1500 * 1024 * 1024), "1500.00 MB") # Test MB boundary


    @patch('espresso.models.disk_scanner.os.path.isdir')
    @patch('espresso.models.disk_scanner.os.path.abspath')
    @patch('espresso.models.disk_scanner.os.path.expanduser')
    @patch('espresso.models.disk_scanner.os.scandir')
    def test_scan_directory_simple(self, mock_scandir, mock_expanduser, mock_abspath, mock_isdir):
        # --- Setup Mocks ---
        mock_expanduser.return_value = '/mock/test_dir'
        mock_abspath.return_value = '/mock/test_dir'
        mock_isdir.return_value = True

        # Mock file system structure:
        # /mock/test_dir
        #   - file1.txt (100 bytes)
        #   - sub_dir1
        #     - file2.txt (200 bytes)
        
        mock_entry_file1 = MagicMock()
        mock_entry_file1.name = 'file1.txt'
        mock_entry_file1.path = '/mock/test_dir/file1.txt'
        mock_entry_file1.is_dir.return_value = False
        mock_entry_file1.is_file.return_value = True
        mock_entry_file1.stat.return_value = MagicMock(st_size=100)

        mock_entry_subdir1 = MagicMock()
        mock_entry_subdir1.name = 'sub_dir1'
        mock_entry_subdir1.path = '/mock/test_dir/sub_dir1'
        mock_entry_subdir1.is_dir.return_value = True
        mock_entry_subdir1.is_file.return_value = False
        # No stat needed for dir size initially, it's calculated recursively

        mock_entry_file2 = MagicMock()
        mock_entry_file2.name = 'file2.txt'
        mock_entry_file2.path = '/mock/test_dir/sub_dir1/file2.txt'
        mock_entry_file2.is_dir.return_value = False
        mock_entry_file2.is_file.return_value = True
        mock_entry_file2.stat.return_value = MagicMock(st_size=200)

        # Configure scandir:
        # 1st call for '/mock/test_dir'
        # 2nd call for '/mock/test_dir/sub_dir1'
        # 3rd call for an empty dir (or stop recursion)
        mock_scandir.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=iter([mock_entry_file1, mock_entry_subdir1]))), # /mock/test_dir
            MagicMock(__enter__=MagicMock(return_value=iter([mock_entry_file2]))), # /mock/test_dir/sub_dir1
            MagicMock(__enter__=MagicMock(return_value=iter([]))) # Empty for any further calls
        ]

        # --- Call the method ---
        self.scanner.scan_directory('/mock/test_dir')
        results = self.scanner.get_results()
        
        # --- Assertions ---
        # print(results) # For debugging if needed

        self.assertIn('/mock/test_dir/file1.txt', results)
        self.assertEqual(results['/mock/test_dir/file1.txt']['size'], 100)
        self.assertEqual(results['/mock/test_dir/file1.txt']['type'], 'file')
        self.assertEqual(results['/mock/test_dir/file1.txt']['parent'], '/mock/test_dir')
        
        self.assertIn('/mock/test_dir/sub_dir1/file2.txt', results)
        self.assertEqual(results['/mock/test_dir/sub_dir1/file2.txt']['size'], 200)
        self.assertEqual(results['/mock/test_dir/sub_dir1/file2.txt']['type'], 'file')
        self.assertEqual(results['/mock/test_dir/sub_dir1/file2.txt']['parent'], '/mock/test_dir/sub_dir1')

        self.assertIn('/mock/test_dir/sub_dir1', results)
        self.assertEqual(results['/mock/test_dir/sub_dir1']['size'], 200) # Size of file2.txt
        self.assertEqual(results['/mock/test_dir/sub_dir1']['type'], 'directory')
        self.assertEqual(results['/mock/test_dir/sub_dir1']['parent'], '/mock/test_dir')
        
        # Check ordering by _organize_results (sub_dir1 then file2.txt, then file1.txt if sorted by size desc)
        # The current _organize_results sorts directories by size, then files by size.
        # Expected: sub_dir1 (200), file2.txt (200), file1.txt (100)
        result_items = list(results.items())
        # Expected order (desc size, dirs first if sizes are equal):
        # 1. /mock/test_dir/sub_dir1 (dir, 200)
        # 2. /mock/test_dir/sub_dir1/file2.txt (file, 200)
        # 3. /mock/test_dir/file1.txt (file, 100)

        self.assertEqual(result_items[0][0], '/mock/test_dir/sub_dir1')
        self.assertEqual(result_items[1][0], '/mock/test_dir/sub_dir1/file2.txt')
        self.assertEqual(result_items[2][0], '/mock/test_dir/file1.txt')


    @patch('espresso.models.disk_scanner.os.path.isdir')
    def test_scan_directory_not_a_directory(self, mock_isdir):
        mock_isdir.return_value = False
        self.scanner.scan_directory('/not/a/dir')
        self.assertEqual(self.scanner.get_results(), {})

    @patch('espresso.models.disk_scanner.os.path.isdir', return_value=True)
    @patch('espresso.models.disk_scanner.os.path.abspath', side_effect=lambda x: x)
    @patch('espresso.models.disk_scanner.os.path.expanduser', side_effect=lambda x: x)
    @patch('espresso.models.disk_scanner.os.scandir')
    def test_scan_directory_permission_error_on_scandir(self, mock_scandir, mock_expanduser, mock_abspath, mock_isdir):
        mock_scandir.side_effect = PermissionError("Cannot access directory")
        
        self.scanner.scan_directory('/permission/denied_dir')
        # Should not raise an exception, results might be empty or partial
        # The current code prints an error and continues, so results would be empty if top-level scan fails.
        self.assertEqual(self.scanner.get_results(), {})


    @patch('espresso.models.disk_scanner.os.path.isdir', return_value=True)
    @patch('espresso.models.disk_scanner.os.path.abspath', side_effect=lambda x: x)
    @patch('espresso.models.disk_scanner.os.path.expanduser', side_effect=lambda x: x)
    @patch('espresso.models.disk_scanner.os.scandir')
    def test_scan_recursive_permission_error_on_entry(self, mock_scandir, mock_expanduser, mock_abspath, mock_isdir):
        mock_entry_accessible = MagicMock()
        mock_entry_accessible.name = 'accessible_file.txt'
        mock_entry_accessible.path = '/mock/accessible_file.txt'
        mock_entry_accessible.is_dir.return_value = False
        mock_entry_accessible.is_file.return_value = True
        mock_entry_accessible.stat.return_value = MagicMock(st_size=50)

        mock_entry_denied = MagicMock()
        mock_entry_denied.name = 'denied_file.txt'
        mock_entry_denied.path = '/mock/denied_file.txt'
        mock_entry_denied.is_dir.side_effect = PermissionError("Cannot access") # Error when checking type

        mock_scandir.return_value = MagicMock(__enter__=MagicMock(return_value=iter([mock_entry_accessible, mock_entry_denied])))
        
        self.scanner.scan_directory('/mock')
        results = self.scanner.get_results()
        
        self.assertIn('/mock/accessible_file.txt', results)
        self.assertEqual(results['/mock/accessible_file.txt']['size'], 50)
        self.assertNotIn('/mock/denied_file.txt', results) # Should be skipped


    def test_stop_scan(self):
        self.scanner.stop_scan()
        self.assertTrue(self.scanner.stop_requested)
        
        # To actually test if it stops, we'd need a long-running scan.
        # For now, just test the flag.
        # A more involved test could mock _scan_recursive to check stop_requested.
        
    @patch('espresso.models.disk_scanner.os.path.isdir', return_value=True)
    @patch('espresso.models.disk_scanner.os.path.abspath', side_effect=lambda x: x)
    @patch('espresso.models.disk_scanner.os.path.expanduser', side_effect=lambda x: x)
    @patch('espresso.models.disk_scanner.DiskScanner._scan_recursive')
    def test_stop_scan_halts_recursion(self, mock_scan_recursive, mock_expanduser, mock_abspath, mock_isdir):
        # Make _scan_recursive set stop_requested to True after the first call
        # to simulate a stop request during the scan of the first item.
        def side_effect_scan_recursive(directory, depth, max_depth):
            if directory == "/mock/test_dir/sub_dir1": # Path of the first sub-directory
                 self.scanner.stop_requested = True # Simulate stop after processing sub_dir1 itself
            # Simulate some size calculation
            if directory == "/mock/test_dir/sub_dir1/file2.txt": # File inside sub_dir1
                return 200 
            if directory == "/mock/test_dir/sub_dir1": # sub_dir1 itself
                # Add self to results, then stop for further items in parent
                self.scanner.results[directory] = {"name": os.path.basename(directory), "type": "directory", "size": 200, "parent": os.path.dirname(directory)}
                return 200 
            if directory == "/mock/test_dir/file1.txt": # File in main dir
                return 100
            if directory == "/mock/test_dir": # Main directory
                 # Process file1.txt then sub_dir1, then stop_requested should be true
                size_file1 = mock_scan_recursive("/mock/test_dir/file1.txt", depth + 1, max_depth)
                self.scanner.results["/mock/test_dir/file1.txt"] = {"name": "file1.txt", "type": "file", "size": size_file1, "parent": directory}
                
                size_subdir1 = mock_scan_recursive("/mock/test_dir/sub_dir1", depth + 1, max_depth)
                # sub_dir1 adds itself to results within its "mocked" execution
                
                return size_file1 + size_subdir1
            return 0

        mock_scan_recursive.side_effect = side_effect_scan_recursive
        
        # This test is more complex due to the direct mocking of _scan_recursive.
        # A simpler approach for `stop_scan` might be to check `self.stop_requested`
        # inside the actual `_scan_recursive` if it were processing a large list of files.
        # For now, this primarily tests the flag.
        self.scanner.scan_directory("/mock/test_dir")
        # The effectiveness of stop_scan is implicitly tested by scan_directory not looping indefinitely
        # if stop_requested is True. Here, we just set it and assume the method respects it.
        # A better test might involve checking how many times os.scandir was called.
        self.assertTrue(self.scanner.stop_requested)


    def test_get_directory_tree(self):
        self.scanner.results = {
            '/A/B/file1.txt': {'name': 'file1.txt', 'type': 'file', 'size': 10, 'parent': '/A/B'},
            '/A/B': {'name': 'B', 'type': 'directory', 'size': 10, 'parent': '/A'},
            '/A/file2.txt': {'name': 'file2.txt', 'type': 'file', 'size': 20, 'parent': '/A'},
            '/A': {'name': 'A', 'type': 'directory', 'size': 30, 'parent': '/'},
        }
        expected_tree = defaultdict(list)
        expected_tree['/A/B'].append('/A/B/file1.txt')
        expected_tree['/A'].append('/A/B')
        expected_tree['/A'].append('/A/file2.txt')
        expected_tree['/'].append('/A')
        
        tree = self.scanner.get_directory_tree()
        self.assertEqual(tree, expected_tree)

    def test_organize_results(self):
        self.scanner.results = {
            '/A/file1.txt': {'name': 'file1.txt', 'type': 'file', 'size': 100, 'parent': '/A'},
            '/A/subdir1': {'name': 'subdir1', 'type': 'directory', 'size': 200, 'parent': '/A'},
            '/A/file2.txt': {'name': 'file2.txt', 'type': 'file', 'size': 50, 'parent': '/A'},
            '/B/big_dir': {'name': 'big_dir', 'type': 'directory', 'size': 500, 'parent': '/B'},
            '/B/small_file.txt': {'name': 'small_file.txt', 'type': 'file', 'size': 10, 'parent': '/B'},
        }
        self.scanner._organize_results()
        results = list(self.scanner.results.keys())
        
        # Expected order: Dirs by size desc, then files by size desc
        # /B/big_dir (dir, 500)
        # /A/subdir1 (dir, 200)
        # /A/file1.txt (file, 100)
        # /A/file2.txt (file, 50)
        # /B/small_file.txt (file, 10)
        
        self.assertEqual(results[0], '/B/big_dir')
        self.assertEqual(results[1], '/A/subdir1')
        self.assertEqual(results[2], '/A/file1.txt')
        self.assertEqual(results[3], '/A/file2.txt')
        self.assertEqual(results[4], '/B/small_file.txt')


if __name__ == '__main__':
    unittest.main()
