import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock GTK and GLib before importing GPUController
mock_gi = MagicMock()
sys.modules['gi'] = mock_gi
sys.modules['gi.repository'] = mock_gi.repository
sys.modules['gi.repository.Gtk'] = MagicMock()
sys.modules['gi.repository.GLib'] = MagicMock()

from espresso.controllers.gpu_controller import GPUController

class TestGPUController(unittest.TestCase):

    def setUp(self):
        self.mock_gpu_panel = MagicMock()
        self.mock_metrics = MagicMock()

        # Default setup for a detected GPU
        self.mock_metrics.get_gpu_type.return_value = "nvidia"
        self.gpu_usage_sample = 60.0
        self.gpu_temp_sample = 70.0
        self.gpu_memory_sample = {"used": 1 * 1024**3, "total": 4 * 1024**3, "percent": 25.0}
        self.gpu_info_sample = {"name": "Test NVIDIA GPU", "load": self.gpu_usage_sample, "temp": self.gpu_temp_sample}

        self.mock_metrics.get_gpu_usage.return_value = self.gpu_usage_sample
        self.mock_metrics.get_gpu_temperature.return_value = self.gpu_temp_sample
        self.mock_metrics.get_gpu_memory.return_value = self.gpu_memory_sample
        self.mock_metrics.get_gpu_info.return_value = self.gpu_info_sample
        
        # Controller is initialized in each test to allow modification of gpu_type mock
        # self.controller = GPUController(self.mock_gpu_panel, self.mock_metrics) 

    def test_gpu_controller_init_with_gpu(self):
        # Test GPUController initialization when a GPU is detected.
        # Ensure mocks are configured for this specific test's expectations
        self.mock_metrics.reset_mock() # Reset from setUp
        self.mock_gpu_panel.reset_mock()
        self.mock_metrics.get_gpu_type.return_value = "nvidia"

        controller = GPUController(self.mock_gpu_panel, self.mock_metrics)

        self.assertEqual(controller.panel, self.mock_gpu_panel)
        self.assertEqual(controller.metrics, self.mock_metrics)
        self.assertEqual(controller.history, [])
        self.assertEqual(controller.max_history, 60)
        self.assertEqual(controller.gpu_type, "nvidia")
        self.mock_metrics.get_gpu_type.assert_called_once() # Called during GPUController.__init__
        self.mock_gpu_panel.set_gpu_type.assert_called_once_with("nvidia")

    def test_gpu_controller_init_no_gpu(self):
        # Test GPUController initialization when no GPU is detected.
        self.mock_metrics.reset_mock() # Reset from setUp
        self.mock_gpu_panel.reset_mock()
        self.mock_metrics.get_gpu_type.return_value = None

        controller = GPUController(self.mock_gpu_panel, self.mock_metrics)
        
        self.assertEqual(controller.gpu_type, None)
        self.mock_metrics.get_gpu_type.assert_called_once() # Called during GPUController.__init__
        self.mock_gpu_panel.set_gpu_type.assert_called_once_with(None)

    def test_update_data_with_gpu(self):
        # Test the update method when a GPU is present.
        self.mock_metrics.reset_mock()
        self.mock_gpu_panel.reset_mock()
        self.mock_metrics.get_gpu_type.return_value = "nvidia" # For controller init
        
        # Re-apply default metric values after reset for the test logic
        self.mock_metrics.get_gpu_usage.return_value = self.gpu_usage_sample
        self.mock_metrics.get_gpu_temperature.return_value = self.gpu_temp_sample
        self.mock_metrics.get_gpu_memory.return_value = self.gpu_memory_sample
        self.mock_metrics.get_gpu_info.return_value = self.gpu_info_sample

        controller = GPUController(self.mock_gpu_panel, self.mock_metrics)
        self.mock_metrics.get_gpu_type.assert_called_once() # From init
        self.mock_metrics.get_gpu_type.reset_mock() # Reset for update calls if necessary (not strictly needed here)


        for i in range(5):
            current_gpu_usage = 10.0 * (i + 1) # 10, 20, 30, 40, 50
            self.mock_metrics.get_gpu_usage.return_value = current_gpu_usage # Update for each iteration
            controller.update()

        self.mock_metrics.get_gpu_usage.assert_called()
        self.assertEqual(self.mock_metrics.get_gpu_usage.call_count, 5)
        self.mock_metrics.get_gpu_temperature.assert_called()
        self.assertEqual(self.mock_metrics.get_gpu_temperature.call_count, 5)
        self.mock_metrics.get_gpu_memory.assert_called()
        self.assertEqual(self.mock_metrics.get_gpu_memory.call_count, 5)
        self.mock_metrics.get_gpu_info.assert_called()
        self.assertEqual(self.mock_metrics.get_gpu_info.call_count, 5)


        self.assertEqual(len(controller.history), 5)
        self.assertEqual(controller.history, [10.0, 20.0, 30.0, 40.0, 50.0])

        self.mock_gpu_panel.update_usage_graph.assert_called_with([10.0, 20.0, 30.0, 40.0, 50.0])
        self.mock_gpu_panel.update_temperature.assert_called_with(self.gpu_temp_sample)
        self.mock_gpu_panel.update_memory_info.assert_called_with(
            self.gpu_memory_sample["used"],
            self.gpu_memory_sample["total"],
            self.gpu_memory_sample["percent"]
        )
        self.mock_gpu_panel.update_gpu_details.assert_called_with(self.gpu_info_sample)
        self.mock_gpu_panel.show_no_gpu_message.assert_not_called()


        # Test history capping
        controller.max_history = 3
        self.mock_metrics.get_gpu_usage.return_value = 60.0
        controller.update() 
        self.assertEqual(controller.history, [40.0, 50.0, 60.0])
        self.mock_gpu_panel.update_usage_graph.assert_called_with([40.0, 50.0, 60.0])

    def test_update_data_no_gpu(self):
        # Test the update method when no GPU is present.
        self.mock_metrics.reset_mock()
        self.mock_gpu_panel.reset_mock()
        self.mock_metrics.get_gpu_type.return_value = None

        controller = GPUController(self.mock_gpu_panel, self.mock_metrics)
        self.mock_metrics.get_gpu_type.assert_called_once() # From init
        self.mock_gpu_panel.set_gpu_type.assert_called_once_with(None) # From init
        
        result = controller.update()

        self.assertTrue(result)
        self.mock_gpu_panel.show_no_gpu_message.assert_called_once()
        
        # Ensure other methods were not called
        self.mock_metrics.get_gpu_usage.assert_not_called()
        self.mock_metrics.get_gpu_temperature.assert_not_called()
        self.mock_metrics.get_gpu_memory.assert_not_called()
        self.mock_metrics.get_gpu_info.assert_not_called()
        
        self.mock_gpu_panel.update_usage_graph.assert_not_called()
        self.mock_gpu_panel.update_temperature.assert_not_called()
        self.mock_gpu_panel.update_memory_info.assert_not_called()
        self.mock_gpu_panel.update_gpu_details.assert_not_called()
        
        self.assertEqual(controller.history, []) # History should remain empty

    def test_update_return_value(self):
        # Test the return value of the update method.
        self.mock_metrics.reset_mock()
        self.mock_gpu_panel.reset_mock()
        self.mock_metrics.get_gpu_type.return_value = "nvidia" # Case with GPU
        controller_with_gpu = GPUController(self.mock_gpu_panel, self.mock_metrics)
        self.assertTrue(controller_with_gpu.update())

        # Reset mocks for the no_gpu case
        self.mock_metrics.reset_mock()
        self.mock_gpu_panel.reset_mock()
        self.mock_metrics.get_gpu_type.return_value = None # Case no GPU
        controller_no_gpu = GPUController(self.mock_gpu_panel, self.mock_metrics)
        self.assertTrue(controller_no_gpu.update())


if __name__ == '__main__':
    unittest.main()
