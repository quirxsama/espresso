"""
Espresso - Ana uygulama kontrolcüsü
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio

from espresso.ui.app_window import AppWindow
from espresso.models.metrics import SystemMetrics
from espresso.controllers.cpu_controller import CPUController
from espresso.controllers.ram_controller import RAMController
from espresso.controllers.gpu_controller import GPUController
from espresso.controllers.disk_controller import DiskController


class AppController:
    """Ana uygulama kontrolcüsü"""
    
    def __init__(self, update_interval=1, theme="dark", scan_home=False):
        self.update_interval = update_interval
        self.theme = theme
        self.scan_home = scan_home
        
        # Modelleri oluştur
        self.metrics = SystemMetrics()
        
        # Uygulama ve pencere oluştur
        self.app = Gtk.Application(application_id="com.espresso.monitor")
        self.app.connect("activate", self._on_activate)
    
    def get_app(self):
        """GTK uygulamasını döndürür"""
        return self.app
    
    def _on_activate(self, app):
        """Uygulama aktifleştiğinde çağrılır"""
        # Ana pencereyi oluştur
        self.window = AppWindow(app, self.theme)
        
        # Alt kontrolcüleri oluştur
        self.cpu_controller = CPUController(self.window.cpu_panel, self.metrics)
        self.ram_controller = RAMController(self.window.ram_panel, self.metrics)
        self.gpu_controller = GPUController(self.window.gpu_panel, self.metrics)
        self.disk_controller = DiskController(self.window.disk_panel, self.metrics, 
                                            scan_home=self.scan_home)
        
        # Periyodik veri güncelleme zamanlayıcısını başlat
        GLib.timeout_add_seconds(self.update_interval, self._update_data)
        
        # Pencereyi göster
        self.window.present()
    
    def _update_data(self):
        """Tüm sistem verilerini günceller"""
        # Metrikleri güncelle
        self.metrics.update_all()
        
        # Kontrolcüleri güncelle
        self.cpu_controller.update()
        self.ram_controller.update()
        self.gpu_controller.update()
        self.disk_controller.update()
        
        # Zamanlayıcıyı devam ettir
        return True
