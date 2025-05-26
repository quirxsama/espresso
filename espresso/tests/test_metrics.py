import unittest
from unittest.mock import patch, MagicMock
from espresso.models.metrics import SystemMetrics

class TestSystemMetrics(unittest.TestCase):

    @patch('espresso.models.metrics.psutil')
    @patch('espresso.models.metrics.subprocess')
    @patch('espresso.models.metrics.pynvml', create=True) # create=True for optional import
    def setUp(self, mock_pynvml, mock_subprocess, mock_psutil):
        self.mock_psutil = mock_psutil
        self.mock_subprocess = mock_subprocess
        self.mock_pynvml = mock_pynvml

        # Configure psutil mocks
        # This side_effect will be consumed by the self.metrics.update_all() call later in setUp
        self.mock_psutil.cpu_percent.side_effect = [
            60.0,  # For the first call (overall cpu_usage = psutil.cpu_percent())
            [40.0, 80.0]  # For the second call (cpu_cores = psutil.cpu_percent(percpu=True))
        ]
        
        mock_vm = MagicMock()
        mock_vm.total = 8 * 1024 * 1024 * 1024  # 8GB
        mock_vm.available = 4 * 1024 * 1024 * 1024 # 4GB
        mock_vm.used = 4 * 1024 * 1024 * 1024 # 4GB
        mock_vm.free = 2 * 1024 * 1024 * 1024 # 2GB - Note: free vs available
        mock_vm.percent = 50.0
        self.mock_psutil.virtual_memory.return_value = mock_vm

        mock_swap = MagicMock()
        mock_swap.total = 2 * 1024 * 1024 * 1024 # 2GB
        mock_swap.used = 1 * 1024 * 1024 * 1024 # 1GB
        mock_swap.free = 1 * 1024 * 1024 * 1024 # 1GB
        mock_swap.percent = 50.0
        self.mock_psutil.swap_memory.return_value = mock_swap

        mock_disk_partition = MagicMock()
        mock_disk_partition.mountpoint = "/"
        mock_disk_partition.fstype = "ext4"
        mock_disk_partition.device = "/dev/sda1"
        self.mock_psutil.disk_partitions.return_value = [mock_disk_partition]
        
        mock_disk_usage = MagicMock()
        mock_disk_usage.total = 100 * 1024 * 1024 * 1024 # 100GB
        mock_disk_usage.used = 50 * 1024 * 1024 * 1024 # 50GB
        mock_disk_usage.free = 50 * 1024 * 1024 * 1024 # 50GB
        mock_disk_usage.percent = 50.0
        self.mock_psutil.disk_usage.return_value = mock_disk_usage

        # Configure subprocess mock for CPU temperature
        self.mock_subprocess.check_output.return_value = "Core 0: +45.0°C\nCore 1: +55.0°C"
        
        # Configure pynvml mock (NVIDIA GPU)
        # self.mock_pynvml.nvmlInit.return_value = None # Or raise an exception to test fallback
        self.mock_pynvml.nvmlDeviceGetHandleByIndex.return_value = "dummy_handle"
        mock_utilization = MagicMock()
        mock_utilization.gpu = 60.0
        self.mock_pynvml.nvmlDeviceGetUtilizationRates.return_value = mock_utilization
        self.mock_pynvml.nvmlDeviceGetTemperature.return_value = 65
        mock_mem_info = MagicMock()
        mock_mem_info.total = 4 * 1024 * 1024 * 1024 # 4GB
        mock_mem_info.used = 1 * 1024 * 1024 * 1024 # 1GB
        mock_mem_info.free = 3 * 1024 * 1024 * 1024 # 3GB
        self.mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem_info
        self.mock_pynvml.nvmlDeviceGetName.return_value = "Mock NVIDIA GPU"

        # Initialize SystemMetrics - this will call _detect_gpu
        # To test NVIDIA, ensure pynvml.nvmlInit doesn't raise an error
        # To test AMD, ensure pynvml.nvmlInit raises an error and rocm-smi mock is set up
        # To test None, ensure both fail
        self.metrics = SystemMetrics()
        self.metrics.update_all() # Populate data using mocks

    def test_initialization(self):
        self.assertIsNotNone(self.metrics)

    def test_get_cpu_usage(self):
        # psutil.cpu_percent is called twice in _update_cpu, once for overall, once for per_cpu
        # The mock needs to handle this. Let's adjust setUp or the test.
        self.mock_psutil.cpu_percent.side_effect = [50.0, [25.0, 75.0]]
        self.metrics._update_cpu() # re-run with side_effect
        usage = self.metrics.get_cpu_usage()
        self.assertIsInstance(usage, float)
        self.assertGreaterEqual(usage, 0)
        self.assertLessEqual(usage, 100)
        self.assertEqual(usage, 50.0)

    def test_get_cpu_temperature(self):
        # Test with lm-sensors success
        self.mock_subprocess.check_output.return_value = "Core 0: +45.0°C\nCore 1: +55.0°C"
        self.metrics._update_cpu()
        temp = self.metrics.get_cpu_temperature()
        self.assertIsInstance(temp, (int, float))
        self.assertEqual(temp, 50.0) # Average of 45 and 55

        # Test with lm-sensors failure (e.g., FileNotFoundError)
        self.mock_subprocess.check_output.side_effect = FileNotFoundError
        self.metrics._update_cpu()
        temp = self.metrics.get_cpu_temperature()
        self.assertEqual(temp, 0) # Default value on failure

    def test_get_cpu_core_usages(self):
        self.mock_psutil.cpu_percent.side_effect = [50.0, [25.0, 75.0]]
        self.metrics._update_cpu()
        core_usages = self.metrics.get_cpu_core_usages()
        self.assertIsInstance(core_usages, list)
        if core_usages: # It can be empty if psutil fails in a specific way
            self.assertTrue(all(isinstance(core, float) for core in core_usages))
            self.assertTrue(all(0 <= core <= 100 for core in core_usages))
        self.assertEqual(core_usages, [25.0, 75.0])


    def test_get_ram_info(self):
        ram_info = self.metrics.get_ram_info()
        self.assertIsInstance(ram_info, dict)
        self.assertIn("total", ram_info)
        self.assertIn("used", ram_info)
        self.assertIn("percent", ram_info)
        self.assertGreaterEqual(ram_info["percent"], 0)
        self.assertLessEqual(ram_info["percent"], 100)
        self.assertEqual(ram_info["used"], 4 * 1024 * 1024 * 1024)

    def test_get_swap_info(self):
        swap_info = self.metrics.get_swap_info()
        self.assertIsInstance(swap_info, dict)
        self.assertIn("total", swap_info)
        self.assertIn("used", swap_info)
        self.assertIn("percent", swap_info)
        self.assertGreaterEqual(swap_info["percent"], 0)
        self.assertLessEqual(swap_info["percent"], 100)
        self.assertEqual(swap_info["used"], 1 * 1024 * 1024 * 1024)
        
    def test_get_disk_info(self):
        disk_info = self.metrics.get_disk_info()
        self.assertIsInstance(disk_info, dict)
        self.assertIn("/", disk_info)
        self.assertEqual(disk_info["/"]["used"], 50 * 1024 * 1024 * 1024)

    # GPU Tests
    # Test NVIDIA GPU detection and metrics
    @patch.object(SystemMetrics, '_detect_gpu')
    def test_get_gpu_info_nvidia(self, mock_detect_gpu):
        # Force NVIDIA detection
        self.metrics.gpu_type = "nvidia" 
        # Ensure pynvml is used as expected
        self.mock_pynvml.nvmlInit.reset_mock() # Reset from initial setUp call
        self.mock_pynvml.nvmlDeviceGetHandleByIndex.reset_mock()

        self.metrics._update_gpu() # Call the GPU update logic

        gpu_info = self.metrics.get_gpu_info()
        self.assertEqual(self.metrics.get_gpu_type(), "nvidia")
        self.assertEqual(gpu_info.get("name"), "Mock NVIDIA GPU")
        self.assertEqual(self.metrics.get_gpu_usage(), 60.0)
        self.assertEqual(self.metrics.get_gpu_temperature(), 65)
        memory = self.metrics.get_gpu_memory()
        self.assertEqual(memory.get("total"), 4 * 1024 * 1024 * 1024)
        self.assertAlmostEqual(memory.get("percent"), 25.0)


    @patch('espresso.models.metrics.os.path.exists', return_value=False) # For AMD /sys/class/drm check
    @patch.object(SystemMetrics, '_detect_gpu') # Mock _detect_gpu to isolate _update_gpu
    def test_get_gpu_info_amd(self, mock_detect_gpu, mock_os_exists):
        # Simulate AMD GPU detection
        self.metrics.gpu_type = "amd"
        self.mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="GPU use (%): 30.0\nTemperature: 70 C")
        
        self.metrics._update_gpu()

        gpu_info = self.metrics.get_gpu_info()
        self.assertEqual(self.metrics.get_gpu_type(), "amd")
        self.assertEqual(gpu_info.get("name"), "AMD GPU") # Default name from _update_amd_gpu
        self.assertEqual(self.metrics.get_gpu_usage(), 30.0)
        self.assertEqual(self.metrics.get_gpu_temperature(), 70)


    @patch('espresso.models.metrics.os.path.exists', return_value=False)
    @patch.object(SystemMetrics, '_detect_gpu')
    def test_get_gpu_info_none(self, mock_detect_gpu, mock_os_exists):
        # Simulate no GPU detected
        self.metrics.gpu_type = None
        self.metrics._update_gpu()

        gpu_info = self.metrics.get_gpu_info()
        self.assertIsNone(self.metrics.get_gpu_type())
        self.assertEqual(gpu_info.get("usage", 0), 0) # Default from get_gpu_usage
        self.assertEqual(gpu_info.get("temp", 0), 0)  # Default from get_gpu_temperature
        self.assertEqual(gpu_info.get("name"), None) # No name if no GPU

if __name__ == '__main__':
    unittest.main()
