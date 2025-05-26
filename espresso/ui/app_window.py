"""
Espresso - Ana uygulama penceresi
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk, Gio

from espresso.ui.cpu_panel import CPUPanel
from espresso.ui.ram_panel import RAMPanel
from espresso.ui.gpu_panel import GPUPanel
from espresso.ui.disk_panel import DiskPanel


class AppWindow(Gtk.ApplicationWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self, app, theme="dark"):
        super().__init__(application=app, title="Espresso Sistem Monitörü")
        
        # Pencere ayarları - yatayda geniş, dikeyde kısa
        self.set_default_size(800, 350)
        self.set_size_request(600, 300)
        
        # Yeniden boyutlandırma sınırları
        self.set_resizable(True)
        
        # Yeniden boyutlandırma animasyonunu yavaşlatmak için
        # GTK4'te doğrudan animasyon kontrolü yok, ancak CSS ile geçiş efekti eklenebilir
        self.add_css_class("slow-resize")
        
        # Sistem başlık çubuğunu kullan
        self.set_titlebar(None)
        
        # Tema ayarları
        self._setup_theme(theme)
        
        # Ana düzen
        self._setup_layout()
    
    def _setup_theme(self, theme):
        """Tema ayarlarını yapar"""
        # CSS sağlayıcısı
        css_provider = Gtk.CssProvider()
        
        # Tema dosyasını yükle
        if theme == "dark":
            css_provider.load_from_data(b"""
                window {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    transition: width 0.3s ease, height 0.3s ease;
                }
                
                .slow-resize {
                    transition: width 0.5s ease-in-out, height 0.5s ease-in-out;
                }
                
                .panel {
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                    min-width: 180px;
                    width: 250px;
                    transition: all 0.3s ease;
                }
                
                .panel-title {
                    font-weight: bold;
                    font-size: 16px;
                    margin-bottom: 8px;
                }
                
                .usage-bar {
                    min-height: 10px;
                    border-radius: 5px;
                }
                
                .usage-bar.low {
                    background-color: #4caf50;
                }
                
                .usage-bar.medium {
                    background-color: #ff9800;
                }
                
                .usage-bar.high {
                    background-color: #f44336;
                }
                
                .temperature.low {
                    color: #4caf50;
                }
                
                .temperature.medium {
                    color: #ff9800;
                }
                
                .temperature.high {
                    color: #f44336;
                }
            """)
        else:
            css_provider.load_from_data(b"""
                window {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                
                .panel {
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
                }
                
                .panel-title {
                    font-weight: bold;
                    font-size: 16px;
                    margin-bottom: 8px;
                }
                
                .usage-bar {
                    min-height: 10px;
                    border-radius: 5px;
                }
                
                .usage-bar.low {
                    background-color: #4caf50;
                }
                
                .usage-bar.medium {
                    background-color: #ff9800;
                }
                
                .usage-bar.high {
                    background-color: #f44336;
                }
                
                .temperature.low {
                    color: #4caf50;
                }
                
                .temperature.medium {
                    color: #ff9800;
                }
                
                .temperature.high {
                    color: #f44336;
                }
            """)
        
        # CSS'i uygula
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def _setup_layout(self):
        """Pencere düzenini oluşturur"""
        # Ana kutu
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)
        
        # Başlık çubuğu ve menü butonu kaldırıldı
        
        # İçerik alanı
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content_box.set_margin_top(8)
        content_box.set_margin_bottom(8)
        content_box.set_margin_start(8)
        content_box.set_margin_end(8)
        content_box.set_hexpand(True)
        content_box.set_vexpand(True)
        main_box.append(content_box)
        
        # Responsive düzen için FlowBox kullanıyoruz
        self.flow_box = Gtk.FlowBox()
        self.flow_box.set_valign(Gtk.Align.START)
        self.flow_box.set_max_children_per_line(4)  # Yatayda tüm panelleri göster
        self.flow_box.set_min_children_per_line(1)  # Dar ekranlarda en az 1 panel
        self.flow_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow_box.set_homogeneous(False)  # Paneller kendi içlerinde küçülebilsin
        self.flow_box.set_column_spacing(8)
        self.flow_box.set_row_spacing(8)
        content_box.append(self.flow_box)
        
        # Panel bileşenlerini oluştur
        self.cpu_panel = CPUPanel()
        self.ram_panel = RAMPanel()
        self.gpu_panel = GPUPanel()
        self.disk_panel = DiskPanel()
        
        # Panelleri FlowBox'a yerleştir
        cpu_flow_child = Gtk.FlowBoxChild()
        cpu_flow_child.set_child(self.cpu_panel)
        self.flow_box.append(cpu_flow_child)
        
        ram_flow_child = Gtk.FlowBoxChild()
        ram_flow_child.set_child(self.ram_panel)
        self.flow_box.append(ram_flow_child)
        
        gpu_flow_child = Gtk.FlowBoxChild()
        gpu_flow_child.set_child(self.gpu_panel)
        self.flow_box.append(gpu_flow_child)
        
        disk_flow_child = Gtk.FlowBoxChild()
        disk_flow_child.set_child(self.disk_panel)
        self.flow_box.append(disk_flow_child)
    
    def _create_menu_model(self):
        """Menü modelini oluşturur"""
        menu_model = Gio.Menu()
        
        # Hakkında menüsü
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about_activate)
        self.add_action(about_action)
        menu_model.append("Hakkında", "win.about")
        
        # Ayarlar menüsü
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self._on_settings_activate)
        self.add_action(settings_action)
        menu_model.append("Ayarlar", "win.settings")
        
        # Çıkış menüsü
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit_activate)
        self.add_action(quit_action)
        menu_model.append("Çıkış", "win.quit")
        
        return menu_model
    
    def _on_about_activate(self, action, parameter):
        """Hakkında iletişim kutusunu gösterir"""
        about_dialog = Adw.AboutWindow(
            transient_for=self,
            application_name="Espresso",
            application_icon="utilities-system-monitor",
            developer_name="Espresso Takımı",
            version="0.1.0",
            developers=["Espresso Geliştiricileri"],
            copyright="© 2025 Espresso Takımı"
        )
        about_dialog.present()
    
    def _on_settings_activate(self, action, parameter):
        """Ayarlar iletişim kutusunu gösterir"""
        # TODO: Ayarlar iletişim kutusu
        pass
    
    def _on_quit_activate(self, action, parameter):
        """Uygulamadan çıkar"""
        self.get_application().quit()
