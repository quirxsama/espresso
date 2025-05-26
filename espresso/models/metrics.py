"""
Espresso - Sistem metrikleri modeli
"""

import os
import psutil
import subprocess
from pathlib import Path


class SystemMetrics:
    """Sistem performans metriklerini toplayan sınıf"""
    
    def __init__(self):
        self.cpu_usage = 0
        self.cpu_temp = 0
        self.cpu_cores = []
        self.ram_info = {}
        self.swap_info = {}
        self.gpu_type = None
        self.gpu_info = {}
        self.disk_info = {}
        
        # GPU türünü belirle
        self._detect_gpu()
    
    def update_all(self):
        """Tüm metrikleri günceller"""
        self._update_cpu()
        self._update_ram()
        self._update_gpu()
        self._update_disk()
    
    def _update_cpu(self):
        """CPU metriklerini günceller"""
        # Genel CPU kullanımı
        self.cpu_usage = psutil.cpu_percent()
        
        # Çekirdek kullanımları
        self.cpu_cores = psutil.cpu_percent(percpu=True)
        
        # CPU sıcaklığı (lm-sensors kullanarak)
        try:
            sensors_output = subprocess.check_output(
                ["sensors"], 
                universal_newlines=True,
                stderr=subprocess.DEVNULL
            )
            
            # Çıktıyı işle ve sıcaklığı bul
            for line in sensors_output.split("\n"):
                if "Core" in line and "°C" in line:
                    temp_str = line.split("+")[1].split("°C")[0].strip()
                    try:
                        temp = float(temp_str)
                        # Birden fazla çekirdek varsa ortalama al
                        if self.cpu_temp == 0:
                            self.cpu_temp = temp
                        else:
                            self.cpu_temp = (self.cpu_temp + temp) / 2
                    except ValueError:
                        pass
        except (subprocess.SubprocessError, FileNotFoundError):
            # lm-sensors yoksa veya çalışmazsa
            self.cpu_temp = 0
    
    def _update_ram(self):
        """RAM metriklerini günceller"""
        # RAM bilgileri
        ram = psutil.virtual_memory()
        self.ram_info = {
            "total": ram.total,
            "available": ram.available,
            "used": ram.used,
            "free": ram.free,
            "percent": ram.percent
        }
        
        # Swap bilgileri
        swap = psutil.swap_memory()
        self.swap_info = {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent
        }
    
    def _detect_gpu(self):
        """GPU türünü tespit eder"""
        # NVIDIA GPU kontrolü
        try:
            import pynvml
            pynvml.nvmlInit()
            self.gpu_type = "nvidia"
            return
        except (ImportError, Exception):
            pass
        
        # AMD GPU kontrolü
        try:
            # rocm-smi veya benzeri bir araç kullanılabilir
            result = subprocess.run(
                ["rocm-smi"], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                self.gpu_type = "amd"
                return
        except (FileNotFoundError, subprocess.SubprocessError):
            pass
        
        # Alternatif AMD kontrolü
        try:
            if os.path.exists("/sys/class/drm/card0/device/vendor"):
                with open("/sys/class/drm/card0/device/vendor", "r") as f:
                    vendor = f.read().strip()
                    if vendor == "0x1002":  # AMD vendor ID
                        self.gpu_type = "amd"
                        return
        except (FileNotFoundError, IOError):
            pass
        
        self.gpu_type = None
    
    def _update_gpu(self):
        """GPU metriklerini günceller"""
        if not self.gpu_type:
            return
        
        if self.gpu_type == "nvidia":
            self._update_nvidia_gpu()
        elif self.gpu_type == "amd":
            self._update_amd_gpu()
    
    def _update_nvidia_gpu(self):
        """NVIDIA GPU metriklerini günceller"""
        try:
            import pynvml
            
            # İlk GPU'yu al (çoklu GPU desteği eklenebilir)
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # GPU kullanımı
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            self.gpu_info["usage"] = utilization.gpu
            
            # GPU sıcaklığı
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            self.gpu_info["temp"] = temp
            
            # GPU belleği
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            self.gpu_info["memory"] = {
                "total": memory.total,
                "used": memory.used,
                "free": memory.free,
                "percent": (memory.used / memory.total) * 100
            }
            
            # GPU modeli
            self.gpu_info["name"] = pynvml.nvmlDeviceGetName(handle)
            
        except (ImportError, Exception):
            self.gpu_info = {
                "usage": 0,
                "temp": 0,
                "memory": {"total": 0, "used": 0, "free": 0, "percent": 0},
                "name": "Unknown NVIDIA GPU"
            }
    
    def _update_amd_gpu(self):
        """AMD GPU metriklerini günceller"""
        # AMD GPU için veri toplama (daha basit)
        self.gpu_info = {
            "usage": 0,
            "temp": 0,
            "memory": {"total": 0, "used": 0, "free": 0, "percent": 0},
            "name": "AMD GPU"
        }
        
        try:
            # rocm-smi veya benzeri bir araç kullanılabilir
            result = subprocess.run(
                ["rocm-smi", "--showuse", "--showtemp"], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Kullanım oranını bul
                for line in output.split("\n"):
                    if "GPU use (%)" in line:
                        try:
                            usage = float(line.split(":")[1].strip())
                            self.gpu_info["usage"] = usage
                        except (ValueError, IndexError):
                            pass
                    
                    # Sıcaklığı bul
                    if "Temperature" in line:
                        try:
                            temp = float(line.split(":")[1].split("c")[0].strip())
                            self.gpu_info["temp"] = temp
                        except (ValueError, IndexError):
                            pass
        except (FileNotFoundError, subprocess.SubprocessError):
            pass
    
    def _update_disk(self):
        """Disk metriklerini günceller"""
        # Ana disk bölümlerini al
        partitions = psutil.disk_partitions()
        self.disk_info = {}
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                self.disk_info[partition.mountpoint] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                    "fstype": partition.fstype,
                    "device": partition.device
                }
            except (PermissionError, OSError):
                # Bazı bölümlere erişim izni olmayabilir
                pass
    
    # Getter metodları
    def get_cpu_usage(self):
        """CPU kullanım yüzdesini döndürür"""
        return self.cpu_usage
    
    def get_cpu_temperature(self):
        """CPU sıcaklığını döndürür"""
        return self.cpu_temp
    
    def get_cpu_core_usages(self):
        """CPU çekirdek kullanımlarını döndürür"""
        return self.cpu_cores
    
    def get_ram_info(self):
        """RAM bilgilerini döndürür"""
        return self.ram_info
    
    def get_swap_info(self):
        """Swap bilgilerini döndürür"""
        return self.swap_info
    
    def get_gpu_type(self):
        """GPU türünü döndürür"""
        return self.gpu_type
    
    def get_gpu_usage(self):
        """GPU kullanım yüzdesini döndürür"""
        return self.gpu_info.get("usage", 0)
    
    def get_gpu_temperature(self):
        """GPU sıcaklığını döndürür"""
        return self.gpu_info.get("temp", 0)
    
    def get_gpu_memory(self):
        """GPU bellek bilgilerini döndürür"""
        return self.gpu_info.get("memory", {"total": 0, "used": 0, "free": 0, "percent": 0})
    
    def get_gpu_info(self):
        """Tüm GPU bilgilerini döndürür"""
        return self.gpu_info
    
    def get_disk_info(self):
        """Disk bilgilerini döndürür"""
        return self.disk_info
