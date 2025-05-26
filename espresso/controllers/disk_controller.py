"""
Espresso - Disk panel kontrolcüsü
"""

import os
import threading
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

from espresso.models.disk_scanner import DiskScanner


class DiskController:
    """Disk paneli kontrolcüsü"""
    
    def __init__(self, disk_panel, metrics, scan_home=False):
        self.panel = disk_panel
        self.metrics = metrics
        self.scan_home = scan_home
        self.scanner = DiskScanner()
        self.scanning = False
        self.scan_thread = None
        
        # Başlangıçta home dizinini taramak isteniyorsa
        if self.scan_home:
            self.start_home_scan()
    
    def update(self):
        """Disk verilerini günceller ve paneli yeniler"""
        # Disk kullanım verilerini al
        disk_info = self.metrics.get_disk_info()
        
        # Panel bileşenlerini güncelle
        self.panel.update_disk_usage(disk_info)
        
        # Tarama durumunu kontrol et
        if self.scanning and self.scan_thread and not self.scan_thread.is_alive():
            self.scanning = False
            self.panel.update_scan_status(False)
            
            # Tarama sonuçlarını göster
            scan_results = self.scanner.get_results()
            self.panel.update_directory_tree(scan_results)
        
        return True
    
    def start_home_scan(self):
        """Home dizini taramasını başlatır"""
        if self.scanning:
            return
        
        self.scanning = True
        self.panel.update_scan_status(True)
        
        # Taramayı ayrı bir iş parçacığında başlat
        home_dir = os.path.expanduser("~")
        self.scan_thread = threading.Thread(
            target=self.scanner.scan_directory,
            args=(home_dir,)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def scan_directory(self, directory):
        """Belirtilen dizini tarar"""
        if self.scanning:
            return
        
        self.scanning = True
        self.panel.update_scan_status(True)
        
        # Taramayı ayrı bir iş parçacığında başlat
        self.scan_thread = threading.Thread(
            target=self.scanner.scan_directory,
            args=(directory,)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()
    
    def stop_scan(self):
        """Devam eden taramayı durdurur"""
        if self.scanning and self.scanner:
            self.scanner.stop_scan()
            self.scanning = False
            self.panel.update_scan_status(False)
