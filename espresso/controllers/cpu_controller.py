"""
Espresso - CPU panel kontrolcüsü
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class CPUController:
    """CPU paneli kontrolcüsü"""
    
    def __init__(self, cpu_panel, metrics):
        self.panel = cpu_panel
        self.metrics = metrics
        self.history = []
        self.max_history = 60  # 60 veri noktası sakla
    
    def update(self):
        """CPU verilerini günceller ve paneli yeniler"""
        # CPU kullanım verilerini al
        cpu_usage = self.metrics.get_cpu_usage()
        cpu_temp = self.metrics.get_cpu_temperature()
        
        # Geçmiş verileri güncelle
        self.history.append(cpu_usage)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Panel bileşenlerini güncelle
        self.panel.update_usage_graph(self.history)
        self.panel.update_temperature(cpu_temp)
        
        # CPU çekirdek bilgilerini güncelle
        core_usages = self.metrics.get_cpu_core_usages()
        self.panel.update_core_info(core_usages)
        
        return True
