import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock GTK and GLib before importing RAMController
mock_gi = MagicMock()
sys.modules['gi'] = mock_gi
sys.modules['gi.repository'] = mock_gi.repository
sys.modules['gi.repository.Gtk'] = MagicMock()
sys.modules['gi.repository.GLib'] = MagicMock()

from espresso.controllers.ram_controller import RAMController

class TestRAMController(unittest.TestCase):

    def setUp(self):
        self.mock_ram_panel = MagicMock()
        self.mock_metrics = MagicMock()

        # Configure default return values for metrics
        self.ram_info_sample = {"used": 2 * 1024**3, "total": 8 * 1024**3, "percent": 25.0}
        self.swap_info_sample = {"used": 1 * 1024**3, "total": 4 * 1024**3, "percent": 25.0}
        self.mock_metrics.get_ram_info.return_value = self.ram_info_sample
        self.mock_metrics.get_swap_info.return_value = self.swap_info_sample
        
        self.controller = RAMController(self.mock_ram_panel, self.mock_metrics)

    def test_ram_controller_init(self):
        # Test RAMController initialization.
        self.assertEqual(self.controller.panel, self.mock_ram_panel)
        self.assertEqual(self.controller.metrics, self.mock_metrics)
        self.assertEqual(self.controller.history, [])
        self.assertEqual(self.controller.max_history, 60)

    def test_update_data(self):
        # Test the update method.
        # Call update multiple times to test history
        for i in range(5):
            current_ram_percent = 10.0 * (i + 1) # 10, 20, 30, 40, 50
            ram_info = {"used": (current_ram_percent/100) * 8 * 1024**3, "total": 8 * 1024**3, "percent": current_ram_percent}
            self.mock_metrics.get_ram_info.return_value = ram_info
            self.controller.update()

        # Check metrics calls
        self.mock_metrics.get_ram_info.assert_called()
        self.assertEqual(self.mock_metrics.get_ram_info.call_count, 5)
        self.mock_metrics.get_swap_info.assert_called()
        self.assertEqual(self.mock_metrics.get_swap_info.call_count, 5) # Called in each update

        # Check history (stores RAM percentage)
        self.assertEqual(len(self.controller.history), 5)
        self.assertEqual(self.controller.history, [10.0, 20.0, 30.0, 40.0, 50.0])

        # Check panel update calls (using the values from the last iteration where ram_info percent was 50.0)
        final_ram_info = {"used": (50.0/100) * 8 * 1024**3, "total": 8 * 1024**3, "percent": 50.0}
        self.mock_ram_panel.update_ram_bar.assert_called_with(
            final_ram_info["used"], 
            final_ram_info["total"], 
            final_ram_info["percent"]
        )
        self.mock_ram_panel.update_swap_bar.assert_called_with(
            self.swap_info_sample["used"], 
            self.swap_info_sample["total"], 
            self.swap_info_sample["percent"]
        )
        self.mock_ram_panel.update_memory_details.assert_called_with(final_ram_info, self.swap_info_sample)

        # Test history capping
        self.controller.max_history = 3
        new_ram_percent = 60.0
        ram_info_update = {"used": (new_ram_percent/100) * 8 * 1024**3, "total": 8 * 1024**3, "percent": new_ram_percent}
        self.mock_metrics.get_ram_info.return_value = ram_info_update
        self.controller.update() # History: [30,40,50] -> [40,50,60]
        
        self.assertEqual(self.controller.history, [40.0, 50.0, 60.0])
        self.mock_ram_panel.update_ram_bar.assert_called_with(
            ram_info_update["used"],
            ram_info_update["total"],
            ram_info_update["percent"]
        )
        
    def test_update_return_value(self):
        # Test the return value of the update method.
        self.assertTrue(self.controller.update())

if __name__ == '__main__':
    unittest.main()
