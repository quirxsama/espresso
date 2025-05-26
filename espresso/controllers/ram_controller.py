"""
Espresso - RAM panel kontrolcüsü
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class RAMController:
    """RAM paneli kontrolcüsü"""
    
    def __init__(self, ram_panel, metrics):
        self.panel = ram_panel
        self.metrics = metrics
        self.history = []
        self.max_history = 60  # 60 veri noktası sakla
    
    def update(self):
        """RAM verilerini günceller ve paneli yeniler"""
        # RAM kullanım verilerini al
        ram_info = self.metrics.get_ram_info()
        swap_info = self.metrics.get_swap_info()
        
        # Geçmiş verileri güncelle
        self.history.append(ram_info["percent"])
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Panel bileşenlerini güncelle
        self.panel.update_ram_bar(
            ram_info["used"], 
            ram_info["total"], 
            ram_info["percent"]
        )
        
        self.panel.update_swap_bar(
            swap_info["used"], 
            swap_info["total"], 
            swap_info["percent"]
        )
        
        # Detaylı bellek bilgilerini güncelle
        self.panel.update_memory_details(ram_info, swap_info)
        
        return True
