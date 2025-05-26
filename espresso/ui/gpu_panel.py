"""
Espresso - GPU panel bileşeni
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class GPUPanel(Gtk.Box):
    """GPU paneli bileşeni"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # CSS sınıfı ekle
        self.add_css_class("panel")
        
        # Panel başlığı
        title_label = Gtk.Label(label="GPU")
        title_label.add_css_class("panel-title")
        title_label.set_halign(Gtk.Align.START)
        self.append(title_label)
        
        # GPU kullanım grafiği
        self.usage_graph = GPUUsageGraph()
        self.append(self.usage_graph)
        
        # GPU sıcaklığı
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
        
        # GPU bellek kullanımı
        memory_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        memory_box.set_margin_top(8)
        self.append(memory_box)
        
        memory_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        memory_box.append(memory_label_box)
        
        memory_label = Gtk.Label(label="Bellek:")
        memory_label.set_halign(Gtk.Align.START)
        memory_label_box.append(memory_label)
        
        self.memory_value = Gtk.Label(label="0 / 0 GB (0%)")
        self.memory_value.set_halign(Gtk.Align.END)
        self.memory_value.set_hexpand(True)
        memory_label_box.append(self.memory_value)
        
        self.memory_bar = Gtk.ProgressBar()
        self.memory_bar.set_fraction(0)
        self.memory_bar.add_css_class("usage-bar")
        self.memory_bar.add_css_class("low")
        memory_box.append(self.memory_bar)
        
        # GPU bilgileri
        info_frame = Gtk.Frame()
        info_frame.set_margin_top(16)
        self.append(info_frame)
        
        self.info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.info_box.set_margin_top(8)
        self.info_box.set_margin_bottom(8)
        self.info_box.set_margin_start(8)
        self.info_box.set_margin_end(8)
        info_frame.set_child(self.info_box)
        
        info_label = Gtk.Label(label="GPU Bilgileri")
        info_label.set_halign(Gtk.Align.START)
        self.info_box.append(info_label)
        
        # GPU bulunamadı mesajı
        self.no_gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.no_gpu_box.set_margin_top(16)
        self.no_gpu_box.set_valign(Gtk.Align.CENTER)
        self.no_gpu_box.set_halign(Gtk.Align.CENTER)
        self.no_gpu_box.set_visible(False)
        
        no_gpu_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        no_gpu_icon.set_pixel_size(48)
        self.no_gpu_box.append(no_gpu_icon)
        
        no_gpu_label = Gtk.Label(label="GPU bulunamadı")
        no_gpu_label.add_css_class("title-3")
        self.no_gpu_box.append(no_gpu_label)
        
        self.append(self.no_gpu_box)
        
        # GPU modeli
        self.model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.model_box.set_margin_top(8)
        self.info_box.append(self.model_box)
        
        model_label = Gtk.Label(label="Model:")
        model_label.set_halign(Gtk.Align.START)
        self.model_box.append(model_label)
        
        self.model_value = Gtk.Label(label="")
        self.model_value.set_halign(Gtk.Align.END)
        self.model_value.set_hexpand(True)
        self.model_box.append(self.model_value)
    
    def set_gpu_type(self, gpu_type):
        """GPU türünü ayarlar"""
        if not gpu_type:
            self.show_no_gpu_message()
        else:
            self.show_gpu_info()
            self.model_value.set_text(gpu_type.upper() + " GPU")
    
    def show_no_gpu_message(self):
        """GPU bulunamadı mesajını gösterir"""
        self.usage_graph.set_visible(False)
        self.info_box.get_parent().set_visible(False)
        self.no_gpu_box.set_visible(True)
    
    def show_gpu_info(self):
        """GPU bilgilerini gösterir"""
        self.usage_graph.set_visible(True)
        self.info_box.get_parent().set_visible(True)
        self.no_gpu_box.set_visible(False)
    
    def update_usage_graph(self, history):
        """GPU kullanım grafiğini günceller"""
        self.usage_graph.update_data(history)
    
    def update_temperature(self, temperature):
        """GPU sıcaklık değerini günceller"""
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
    
    def update_memory_info(self, used, total, percent):
        """GPU bellek bilgilerini günceller"""
        # Değerleri GB'a dönüştür
        used_gb = used / (1024 * 1024 * 1024)
        total_gb = total / (1024 * 1024 * 1024)
        
        # Değerleri güncelle
        self.memory_value.set_text(f"{used_gb:.1f} / {total_gb:.1f} GB ({percent:.1f}%)")
        self.memory_bar.set_fraction(percent / 100)
        
        # Renk sınıfını güncelle
        self.memory_bar.remove_css_class("low")
        self.memory_bar.remove_css_class("medium")
        self.memory_bar.remove_css_class("high")
        
        if percent < 50:
            self.memory_bar.add_css_class("low")
        elif percent < 80:
            self.memory_bar.add_css_class("medium")
        else:
            self.memory_bar.add_css_class("high")
    
    def update_gpu_details(self, gpu_info):
        """GPU detay bilgilerini günceller"""
        # GPU modeli
        if "name" in gpu_info:
            self.model_value.set_text(gpu_info["name"])


class GPUUsageGraph(Gtk.DrawingArea):
    """GPU kullanım grafiği bileşeni"""
    
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
        cr.set_source_rgba(0.9, 0.5, 0.1, 1.0)
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
        cr.set_source_rgba(0.9, 0.5, 0.1, 0.3)
        cr.fill()
