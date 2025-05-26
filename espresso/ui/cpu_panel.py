"""
Espresso - CPU panel bileşeni
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class CPUPanel(Gtk.Box):
    """CPU paneli bileşeni"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # CSS sınıfı ekle
        self.add_css_class("panel")
        
        # Panel başlığı
        title_label = Gtk.Label(label="CPU")
        title_label.add_css_class("panel-title")
        title_label.set_halign(Gtk.Align.START)
        self.append(title_label)
        
        # CPU kullanım grafiği
        self.usage_graph = CPUUsageGraph()
        self.append(self.usage_graph)
        
        # CPU sıcaklığı
        temp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        temp_box.set_margin_top(8)
        self.append(temp_box)
        
        temp_label = Gtk.Label(label="Sıcaklık:")
        temp_label.set_halign(Gtk.Align.START)
        temp_box.append(temp_label)
        
        self.temp_value = Gtk.Label(label="0°C")
        self.temp_value.add_css_class("temperature")
        self.temp_value.add_css_class("low")
        self.temp_value.set_halign(Gtk.Align.END)
        self.temp_value.set_hexpand(True)
        temp_box.append(self.temp_value)
        
        # CPU çekirdek bilgileri
        cores_frame = Gtk.Frame()
        cores_frame.set_margin_top(8)
        self.append(cores_frame)
        
        cores_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        cores_box.set_margin_top(8)
        cores_box.set_margin_bottom(8)
        cores_box.set_margin_start(8)
        cores_box.set_margin_end(8)
        cores_frame.set_child(cores_box)
        
        cores_label = Gtk.Label(label="Çekirdekler")
        cores_label.set_halign(Gtk.Align.START)
        cores_box.append(cores_label)
        
        # Çekirdek kullanım çubukları
        self.core_bars = []
        self.core_labels = []
        
        # Varsayılan olarak 4 çekirdek göster
        for i in range(4):
            core_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            core_box.set_margin_top(4)
            cores_box.append(core_box)
            
            core_label = Gtk.Label(label=f"Çekirdek {i+1}:")
            core_label.set_halign(Gtk.Align.START)
            core_label.set_width_chars(10)
            core_box.append(core_label)
            self.core_labels.append(core_label)
            
            progress_bar = Gtk.ProgressBar()
            progress_bar.set_fraction(0)
            progress_bar.add_css_class("usage-bar")
            progress_bar.add_css_class("low")
            progress_bar.set_hexpand(True)
            core_box.append(progress_bar)
            self.core_bars.append(progress_bar)
    
    def update_usage_graph(self, history):
        """CPU kullanım grafiğini günceller"""
        self.usage_graph.update_data(history)
    
    def update_temperature(self, temperature):
        """CPU sıcaklık değerini günceller"""
        # Sıcaklık değerini güncelle
        self.temp_value.set_text(f"{temperature:.1f}°C")
        
        # Sıcaklık rengini güncelle
        self.temp_value.remove_css_class("low")
        self.temp_value.remove_css_class("medium")
        self.temp_value.remove_css_class("high")
        
        if temperature < 60:
            self.temp_value.add_css_class("low")
        elif temperature < 80:
            self.temp_value.add_css_class("medium")
        else:
            self.temp_value.add_css_class("high")
    
    def update_core_info(self, core_usages):
        """CPU çekirdek kullanım bilgilerini günceller"""
        # Çekirdek sayısını kontrol et ve gerekirse yeni çubuklar ekle
        if len(core_usages) > len(self.core_bars):
            # Ek çekirdekler için yeni çubuklar ekle
            parent = self.core_bars[0].get_parent().get_parent()
            
            for i in range(len(self.core_bars), len(core_usages)):
                core_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                core_box.set_margin_top(4)
                parent.append(core_box)
                
                core_label = Gtk.Label(label=f"Çekirdek {i+1}:")
                core_label.set_halign(Gtk.Align.START)
                core_label.set_width_chars(10)
                core_box.append(core_label)
                self.core_labels.append(core_label)
                
                progress_bar = Gtk.ProgressBar()
                progress_bar.set_fraction(0)
                progress_bar.add_css_class("usage-bar")
                progress_bar.add_css_class("low")
                progress_bar.set_hexpand(True)
                core_box.append(progress_bar)
                self.core_bars.append(progress_bar)
        
        # Çekirdek kullanım değerlerini güncelle
        for i, usage in enumerate(core_usages):
            if i < len(self.core_bars):
                # İlerleme çubuğunu güncelle
                self.core_bars[i].set_fraction(usage / 100)
                
                # Renk sınıfını güncelle
                self.core_bars[i].remove_css_class("low")
                self.core_bars[i].remove_css_class("medium")
                self.core_bars[i].remove_css_class("high")
                
                if usage < 50:
                    self.core_bars[i].add_css_class("low")
                elif usage < 80:
                    self.core_bars[i].add_css_class("medium")
                else:
                    self.core_bars[i].add_css_class("high")


class CPUUsageGraph(Gtk.DrawingArea):
    """CPU kullanım grafiği bileşeni"""
    
    def __init__(self):
        super().__init__()
        
        # Veri noktaları
        self.data = []
        self.max_data_points = 60
        
        # Çizim alanı ayarları
        self.set_content_width(200)
        self.set_content_height(100)
        self.set_draw_func(self._draw_func)
        self.set_hexpand(True)
    
    def update_data(self, data):
        """Grafik verilerini günceller"""
        self.data = data.copy()
        self.queue_draw()
    
    def _draw_func(self, area, cr, width, height):
        """Grafik çizim fonksiyonu"""
        # Arka planı temizle
        cr.set_source_rgba(0.2, 0.2, 0.2, 0.5)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        # Veri yoksa çizme
        if not self.data:
            return
        
        # Izgara çiz
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.2)
        cr.set_line_width(1)
        
        # Yatay ızgaralar
        for i in range(1, 4):
            y = height * i / 4
            cr.move_to(0, y)
            cr.line_to(width, y)
            cr.stroke()
        
        # Dikey ızgaralar
        for i in range(1, 6):
            x = width * i / 6
            cr.move_to(x, 0)
            cr.line_to(x, height)
            cr.stroke()
        
        # Veriyi çiz
        cr.set_source_rgba(0.2, 0.7, 0.9, 1.0)
        cr.set_line_width(2)
        
        # Veri noktalarını ölçeklendir
        point_width = width / min(self.max_data_points, len(self.data))
        
        # İlk noktayı ayarla
        cr.move_to(0, height - (self.data[0] / 100) * height)
        
        # Diğer noktaları çiz
        for i, value in enumerate(self.data):
            x = i * point_width
            y = height - (value / 100) * height
            cr.line_to(x, y)
        
        # Çizgiyi çiz
        cr.stroke()
        
        # Dolgu ekle
        cr.line_to(width, height)
        cr.line_to(0, height)
        cr.close_path()
        cr.set_source_rgba(0.2, 0.7, 0.9, 0.3)
        cr.fill()
