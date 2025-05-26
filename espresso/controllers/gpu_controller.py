"""
Espresso - GPU panel kontrolcüsü
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class GPUController:
    """GPU paneli kontrolcüsü"""
    
    def __init__(self, gpu_panel, metrics):
        self.panel = gpu_panel
        self.metrics = metrics
        self.history = []
        self.max_history = 60  # 60 veri noktası sakla
        
        # GPU türünü belirle (NVIDIA, AMD veya yok)
        self.gpu_type = self.metrics.get_gpu_type()
        self.panel.set_gpu_type(self.gpu_type)
    
    def update(self):
        """GPU verilerini günceller ve paneli yeniler"""
        # GPU bulunamadıysa güncelleme yapma
        if not self.gpu_type:
            self.panel.show_no_gpu_message()
            return True
        
        # GPU kullanım verilerini al
        gpu_usage = self.metrics.get_gpu_usage()
        gpu_temp = self.metrics.get_gpu_temperature()
        gpu_memory = self.metrics.get_gpu_memory()
        
        # Geçmiş verileri güncelle
        self.history.append(gpu_usage)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Panel bileşenlerini güncelle
        self.panel.update_usage_graph(self.history)
        self.panel.update_temperature(gpu_temp)
        self.panel.update_memory_info(
            gpu_memory["used"],
            gpu_memory["total"],
            gpu_memory["percent"]
        )
        
        # Ek GPU bilgilerini güncelle
        gpu_info = self.metrics.get_gpu_info()
        self.panel.update_gpu_details(gpu_info)
        
        return True
