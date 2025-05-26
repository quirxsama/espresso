import unittest
from unittest.mock import MagicMock, patch, call
import sys
import threading # DiskController uses threading directly

# Mock GTK and GLib before importing DiskController
mock_gi = MagicMock()
sys.modules['gi'] = mock_gi
sys.modules['gi.repository'] = mock_gi.repository
sys.modules['gi.repository.Gtk'] = MagicMock()
sys.modules['gi.repository.GLib'] = MagicMock()
sys.modules['gi.repository.Gio'] = MagicMock() # DiskController imports Gio

from espresso.controllers.disk_controller import DiskController

@patch('espresso.controllers.disk_controller.os.path.expanduser')
@patch('espresso.controllers.disk_controller.threading.Thread')
@patch('espresso.controllers.disk_controller.DiskScanner') # This is the new/moved patch
class TestDiskController(unittest.TestCase):

    def setUp(self, MockDiskScanner_class, MockThread, mock_expanduser):
        self.mock_disk_panel = MagicMock()
        self.mock_metrics = MagicMock()
        
        MockDiskScanner_class.reset_mock() # Reset the mock class itself
        self.mock_scanner_instance = MockDiskScanner_class.return_value 
        self.mock_scanner_instance.reset_mock() # Reset the instance for good measure

        # Default metric values
        # Define GB for clarity, or use bytes
        GB = 1024 * 1024 * 1024
        self.disk_info_sample = {"/": {"total": 100*GB, "used": 50*GB, "percent": 50.0}}
        self.mock_metrics.get_disk_info.return_value = self.disk_info_sample
        
        # Scan results
        self.scan_results_sample = {"/home/user/file.txt": {"size": 10*GB}}
        self.mock_scanner_instance.get_results.return_value = self.scan_results_sample


    def test_disk_controller_init_no_scan_home(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test initialization when scan_home is False.
        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=False)
        
        self.assertEqual(controller.panel, self.mock_disk_panel)
        self.assertEqual(controller.metrics, self.mock_metrics)
        self.assertEqual(controller.scanner, self.mock_scanner_instance)
        self.assertFalse(controller.scanning)
        self.assertIsNone(controller.scan_thread)
        MockDiskScanner_class.assert_called_once() # Scanner is always instantiated
        MockThread.assert_not_called() # No thread started if scan_home is False

    def test_disk_controller_init_with_scan_home(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test initialization when scan_home is True.
        mock_expanduser.return_value = "/home/mockuser"
        mock_thread_instance = MockThread.return_value # Mock for the thread object

        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=True)
        
        mock_expanduser.assert_called_once_with("~")
        MockThread.assert_called_once_with(
            target=self.mock_scanner_instance.scan_directory,
            args=("/home/mockuser",)
        )
        self.assertEqual(mock_thread_instance.daemon, True) # Check if set
        mock_thread_instance.start.assert_called_once()
        self.assertTrue(controller.scanning)
        self.mock_disk_panel.update_scan_status.assert_called_once_with(True)

    def test_update_disk_usage_only(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test update method when no scan is active or finishing.
        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=False) # Ensure no initial scan
        controller.scanning = False # Ensure no scan is considered active
        
        result = controller.update()
        
        self.assertTrue(result)
        self.mock_metrics.get_disk_info.assert_called_once()
        self.mock_disk_panel.update_disk_usage.assert_called_once_with(self.disk_info_sample)
        self.mock_scanner_instance.get_results.assert_not_called()
        self.mock_disk_panel.update_directory_tree.assert_not_called()

    def test_update_scan_finishes(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test update method when a scan has just finished.
        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=False) # No initial scan
        
        # Simulate an active scan thread that is no longer alive
        mock_thread_instance = MagicMock()
        mock_thread_instance.is_alive.return_value = False 
        controller.scan_thread = mock_thread_instance
        controller.scanning = True # Mark as scanning

        controller.update()

        self.assertFalse(controller.scanning) # Should be set to False
        self.mock_disk_panel.update_scan_status.assert_called_with(False)
        self.mock_scanner_instance.get_results.assert_called_once()
        self.mock_disk_panel.update_directory_tree.assert_called_once_with(self.scan_results_sample)

    def test_update_scan_still_running(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test update method when a scan is still running.
        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=False) # No initial scan

        mock_thread_instance = MagicMock()
        mock_thread_instance.is_alive.return_value = True # Still alive
        controller.scan_thread = mock_thread_instance
        controller.scanning = True

        # Reset panel mock as update_scan_status is called in init if scan_home=True
        # For this test, we want to ensure it's not called during *this* update
        self.mock_disk_panel.reset_mock()

        controller.update()

        self.assertTrue(controller.scanning) # Should remain true
        self.mock_disk_panel.update_scan_status.assert_not_called() # Not called if status doesn't change from true
        self.mock_scanner_instance.get_results.assert_not_called()
        self.mock_disk_panel.update_directory_tree.assert_not_called()

    def test_start_home_scan(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test starting a home directory scan.
        mock_expanduser.return_value = "/home/mockuser"
        mock_thread_instance = MockThread.return_value
        
        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=False) # No initial scan
        
        # Clear any potential calls from init if scan_home was true in a prior version
        self.mock_disk_panel.reset_mock() 
        MockThread.reset_mock()

        controller.start_home_scan()

        self.assertTrue(controller.scanning)
        self.mock_disk_panel.update_scan_status.assert_called_once_with(True)
        mock_expanduser.assert_called_once_with("~")
        MockThread.assert_called_once_with(
            target=self.mock_scanner_instance.scan_directory,
            args=("/home/mockuser",)
        )
        self.assertEqual(mock_thread_instance.daemon, True)
        mock_thread_instance.start.assert_called_once()

        # Test does not start if already scanning
        MockThread.reset_mock()
        self.mock_disk_panel.update_scan_status.reset_mock()
        controller.start_home_scan() # Should do nothing
        MockThread.assert_not_called()
        self.mock_disk_panel.update_scan_status.assert_not_called()


    def test_scan_directory_custom(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test starting a scan for a custom directory.
        mock_thread_instance = MockThread.return_value
        test_dir = "/mnt/data"
        
        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=False)
        # Clear any potential calls from init
        self.mock_disk_panel.reset_mock() 
        MockThread.reset_mock()

        controller.scan_directory(test_dir)

        self.assertTrue(controller.scanning)
        self.mock_disk_panel.update_scan_status.assert_called_once_with(True)
        MockThread.assert_called_once_with(
            target=self.mock_scanner_instance.scan_directory,
            args=(test_dir,)
        )
        self.assertEqual(mock_thread_instance.daemon, True)
        mock_thread_instance.start.assert_called_once()
        mock_expanduser.assert_not_called() # Not for custom dir

    def test_stop_scan(self, MockDiskScanner_class, MockThread, mock_expanduser):
        # Test stopping an ongoing scan.
        controller = DiskController(self.mock_disk_panel, self.mock_metrics, scan_home=False)
         # Clear any potential calls from init
        self.mock_disk_panel.reset_mock()
        
        # Simulate ongoing scan
        controller.scanning = True
        controller.scanner = self.mock_scanner_instance # Ensure it has the mocked scanner

        controller.stop_scan()

        self.assertFalse(controller.scanning)
        self.mock_scanner_instance.stop_scan.assert_called_once()
        self.mock_disk_panel.update_scan_status.assert_called_once_with(False)

        # Test does nothing if not scanning
        self.mock_scanner_instance.stop_scan.reset_mock()
        self.mock_disk_panel.update_scan_status.reset_mock()
        controller.stop_scan() # Already stopped
        self.mock_scanner_instance.stop_scan.assert_not_called()
        self.mock_disk_panel.update_scan_status.assert_not_called()


if __name__ == '__main__':
    unittest.main()
