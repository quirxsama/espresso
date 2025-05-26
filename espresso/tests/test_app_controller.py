import unittest
from unittest.mock import MagicMock, patch, call
import sys

# Mock GTK and GLib before importing AppController
# This is crucial as AppController imports them at the module level.
mock_gi = MagicMock()
mock_gi.repository.Gtk = MagicMock()
mock_gi.repository.GLib = MagicMock()
mock_gi.repository.Gio = MagicMock()

# Apply the mock to sys.modules
sys.modules['gi'] = mock_gi
sys.modules['gi.repository'] = mock_gi.repository
sys.modules['gi.repository.Gtk'] = mock_gi.repository.Gtk
sys.modules['gi.repository.GLib'] = mock_gi.repository.GLib
sys.modules['gi.repository.Gio'] = mock_gi.repository.Gio


# Now import the modules that depend on Gtk/GLib
from espresso.controllers.app_controller import AppController
# We also need to ensure that other controllers are patched if they import Gtk themselves
# For now, assume their direct Gtk usage is minimal or handled by their own tests.

@patch('espresso.controllers.app_controller.AppWindow')
@patch('espresso.controllers.app_controller.SystemMetrics')
@patch('espresso.controllers.app_controller.CPUController')
@patch('espresso.controllers.app_controller.RAMController')
@patch('espresso.controllers.app_controller.GPUController')
@patch('espresso.controllers.app_controller.DiskController')
class TestAppController(unittest.TestCase):

    def setUp(self):
        # Reset mocks for GLib and Gtk if they are stateful across tests
        mock_gi.repository.Gtk.Application.reset_mock()
        mock_gi.repository.GLib.timeout_add_seconds.reset_mock()

    def test_app_controller_init(self, MockDiskController, MockGPUController, MockRAMController, MockCPUController, MockSystemMetrics, MockAppWindow):
        # Test AppController initialization.
        app_controller = AppController(update_interval=2, theme="light", scan_home=True)

        self.assertEqual(app_controller.update_interval, 2)
        self.assertEqual(app_controller.theme, "light")
        self.assertEqual(app_controller.scan_home, True)
        MockSystemMetrics.assert_called_once()
        mock_gi.repository.Gtk.Application.assert_called_once_with(application_id="com.espresso.monitor")
        app_controller.app.connect.assert_called_once_with("activate", app_controller._on_activate)

    def test_on_activate(self, MockDiskController, MockGPUController, MockRAMController, MockCPUController, MockSystemMetrics, MockAppWindow):
        # Test the _on_activate method.
        mock_app_instance = MagicMock() # Mock for the Gtk.Application instance passed to _on_activate
        
        app_controller = AppController(scan_home=True) # Use default interval and theme

        # Mock instances that would be created in _on_activate
        mock_window_instance = MockAppWindow.return_value
        mock_metrics_instance = MockSystemMetrics.return_value
        
        # Call _on_activate
        app_controller._on_activate(mock_app_instance)

        # Check that AppWindow was initialized
        MockAppWindow.assert_called_once_with(mock_app_instance, app_controller.theme)
        
        # Check that controllers were initialized with the window's panels and metrics
        MockCPUController.assert_called_once_with(mock_window_instance.cpu_panel, mock_metrics_instance)
        MockRAMController.assert_called_once_with(mock_window_instance.ram_panel, mock_metrics_instance)
        MockGPUController.assert_called_once_with(mock_window_instance.gpu_panel, mock_metrics_instance)
        MockDiskController.assert_called_once_with(mock_window_instance.disk_panel, mock_metrics_instance, scan_home=True)
        
        # Check that GLib.timeout_add_seconds was called
        mock_gi.repository.GLib.timeout_add_seconds.assert_called_once_with(app_controller.update_interval, app_controller._update_data)
        
        # Check that the window was presented
        mock_window_instance.present.assert_called_once()

    def test_update_data(self, MockDiskController, MockGPUController, MockRAMController, MockCPUController, MockSystemMetrics, MockAppWindow):
        # Test the _update_data method.
        app_controller = AppController()
        
        # To test _update_data, we need to simulate the state after _on_activate
        # where sub-controllers are instantiated.
        mock_metrics_instance = MockSystemMetrics.return_value
        app_controller.metrics = mock_metrics_instance # Assign the mocked instance

        # Assign mocked controller instances
        app_controller.cpu_controller = MockCPUController.return_value
        app_controller.ram_controller = MockRAMController.return_value
        app_controller.gpu_controller = MockGPUController.return_value
        app_controller.disk_controller = MockDiskController.return_value
        
        # Call _update_data
        result = app_controller._update_data()

        # Check that metrics.update_all was called
        mock_metrics_instance.update_all.assert_called_once()
        
        # Check that update methods of sub-controllers were called
        app_controller.cpu_controller.update.assert_called_once()
        app_controller.ram_controller.update.assert_called_once()
        app_controller.gpu_controller.update.assert_called_once()
        app_controller.disk_controller.update.assert_called_once()
        
        self.assertTrue(result) # Should return True to continue the timer

if __name__ == '__main__':
    unittest.main()
