import unittest
from unittest.mock import MagicMock, patch, call
import sys

# Mock GTK and GLib before importing CPUController
mock_gi = MagicMock()
sys.modules['gi'] = mock_gi
sys.modules['gi.repository'] = mock_gi.repository
sys.modules['gi.repository.Gtk'] = MagicMock()
sys.modules['gi.repository.GLib'] = MagicMock()

from espresso.controllers.cpu_controller import CPUController

class TestCPUController(unittest.TestCase):

    def setUp(self):
        self.mock_cpu_panel = MagicMock()
        self.mock_metrics = MagicMock()
        
        # Configure default return values for metrics
        self.mock_metrics.get_cpu_usage.return_value = 50.0
        self.mock_metrics.get_cpu_temperature.return_value = 65.0
        self.mock_metrics.get_cpu_core_usages.return_value = [25.0, 75.0]
        
        self.controller = CPUController(self.mock_cpu_panel, self.mock_metrics)

    def test_cpu_controller_init(self):
        # Test CPUController initialization.
        self.assertEqual(self.controller.panel, self.mock_cpu_panel)
        self.assertEqual(self.controller.metrics, self.mock_metrics)
        self.assertEqual(self.controller.history, [])
        self.assertEqual(self.controller.max_history, 60)

    def test_update_data(self):
        # Test the update method.
        # Call update multiple times to test history
        for i in range(5):
            self.mock_metrics.get_cpu_usage.return_value = 10.0 * (i + 1) # 10, 20, 30, 40, 50
            self.controller.update()

        # Check metrics calls
        self.mock_metrics.get_cpu_usage.assert_called()
        self.assertEqual(self.mock_metrics.get_cpu_usage.call_count, 5)
        self.mock_metrics.get_cpu_temperature.assert_called()
        self.assertEqual(self.mock_metrics.get_cpu_temperature.call_count, 5)
        self.mock_metrics.get_cpu_core_usages.assert_called()
        self.assertEqual(self.mock_metrics.get_cpu_core_usages.call_count, 5)

        # Check history
        self.assertEqual(len(self.controller.history), 5)
        self.assertEqual(self.controller.history, [10.0, 20.0, 30.0, 40.0, 50.0])

        # Check panel update calls (only the last call's arguments are checked by default with assert_called_with)
        self.mock_cpu_panel.update_usage_graph.assert_called_with([10.0, 20.0, 30.0, 40.0, 50.0])
        self.mock_cpu_panel.update_temperature.assert_called_with(65.0) # Temp is constant in this test setup after loop
        self.mock_cpu_panel.update_core_info.assert_called_with([25.0, 75.0]) # Core usages also constant

        # Test history capping
        self.controller.max_history = 3
        self.mock_metrics.get_cpu_usage.return_value = 60.0
        self.controller.update() # History: [30,40,50] -> [40,50,60]
        self.assertEqual(self.controller.history, [40.0, 50.0, 60.0])
        self.mock_cpu_panel.update_usage_graph.assert_called_with([40.0, 50.0, 60.0])
        
        self.mock_metrics.get_cpu_usage.return_value = 70.0
        self.controller.update() # History: [40,50,60] -> [50,60,70]
        self.assertEqual(self.controller.history, [50.0, 60.0, 70.0])
        self.mock_cpu_panel.update_usage_graph.assert_called_with([50.0, 60.0, 70.0])


    def test_update_return_value(self):
        # Test the return value of the update method.
        self.assertTrue(self.controller.update())

if __name__ == '__main__':
    unittest.main()
