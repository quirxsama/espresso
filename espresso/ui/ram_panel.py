"""
Espresso - RAM panel bileşeni
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class RAMPanel(Gtk.Box):
    """RAM paneli bileşeni"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # CSS sınıfı ekle
        self.add_css_class("panel")
        
        # Panel başlığı
        title_label = Gtk.Label(label="RAM")
        title_label.add_css_class("panel-title")
        title_label.set_halign(Gtk.Align.START)
        self.append(title_label)
        
        # RAM kullanım çubuğu
        ram_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ram_box.set_margin_top(8)
        self.append(ram_box)
        
        ram_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        ram_box.append(ram_label_box)
        
        ram_label = Gtk.Label(label="Bellek:")
        ram_label.set_halign(Gtk.Align.START)
        ram_label_box.append(ram_label)
        
        self.ram_value = Gtk.Label(label="0 / 0 GB (0%)")
        self.ram_value.set_halign(Gtk.Align.END)
        self.ram_value.set_hexpand(True)
        ram_label_box.append(self.ram_value)
        
        self.ram_bar = Gtk.ProgressBar()
        self.ram_bar.set_fraction(0)
        self.ram_bar.add_css_class("usage-bar")
        self.ram_bar.add_css_class("low")
        ram_box.append(self.ram_bar)
        
        # Swap kullanım çubuğu
        swap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        swap_box.set_margin_top(16)
        self.append(swap_box)
        
        swap_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        swap_box.append(swap_label_box)
        
        swap_label = Gtk.Label(label="Swap:")
        swap_label.set_halign(Gtk.Align.START)
        swap_label_box.append(swap_label)
        
        self.swap_value = Gtk.Label(label="0 / 0 GB (0%)")
        self.swap_value.set_halign(Gtk.Align.END)
        self.swap_value.set_hexpand(True)
        swap_label_box.append(self.swap_value)
        
        self.swap_bar = Gtk.ProgressBar()
        self.swap_bar.set_fraction(0)
        self.swap_bar.add_css_class("usage-bar")
        self.swap_bar.add_css_class("low")
        swap_box.append(self.swap_bar)
        
        # Detaylı bellek bilgileri
        details_frame = Gtk.Frame()
        details_frame.set_margin_top(16)
        self.append(details_frame)
        
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        details_box.set_margin_top(8)
        details_box.set_margin_bottom(8)
        details_box.set_margin_start(8)
        details_box.set_margin_end(8)
        details_frame.set_child(details_box)
        
        details_label = Gtk.Label(label="Detaylı Bilgiler")
        details_label.set_halign(Gtk.Align.START)
        details_box.append(details_label)
        
        # Detay satırları
        self.details_grid = Gtk.Grid()
        self.details_grid.set_column_spacing(8)
        self.details_grid.set_row_spacing(4)
        self.details_grid.set_margin_top(8)
        details_box.append(self.details_grid)
        
        # Toplam RAM
        total_label = Gtk.Label(label="Toplam RAM:")
        total_label.set_halign(Gtk.Align.START)
        self.details_grid.attach(total_label, 0, 0, 1, 1)
        
        self.total_value = Gtk.Label(label="0 GB")
        self.total_value.set_halign(Gtk.Align.END)
        self.details_grid.attach(self.total_value, 1, 0, 1, 1)
        
        # Kullanılan RAM
        used_label = Gtk.Label(label="Kullanılan:")
        used_label.set_halign(Gtk.Align.START)
        self.details_grid.attach(used_label, 0, 1, 1, 1)
        
        self.used_value = Gtk.Label(label="0 GB")
        self.used_value.set_halign(Gtk.Align.END)
        self.details_grid.attach(self.used_value, 1, 1, 1, 1)
        
        # Boş RAM
        free_label = Gtk.Label(label="Boş:")
        free_label.set_halign(Gtk.Align.START)
        self.details_grid.attach(free_label, 0, 2, 1, 1)
        
        self.free_value = Gtk.Label(label="0 GB")
        self.free_value.set_halign(Gtk.Align.END)
        self.details_grid.attach(self.free_value, 1, 2, 1, 1)
        
        # Toplam Swap
        swap_total_label = Gtk.Label(label="Toplam Swap:")
        swap_total_label.set_halign(Gtk.Align.START)
        self.details_grid.attach(swap_total_label, 0, 3, 1, 1)
        
        self.swap_total_value = Gtk.Label(label="0 GB")
        self.swap_total_value.set_halign(Gtk.Align.END)
        self.details_grid.attach(self.swap_total_value, 1, 3, 1, 1)
        
        # Kullanılan Swap
        swap_used_label = Gtk.Label(label="Kullanılan Swap:")
        swap_used_label.set_halign(Gtk.Align.START)
        self.details_grid.attach(swap_used_label, 0, 4, 1, 1)
        
        self.swap_used_value = Gtk.Label(label="0 GB")
        self.swap_used_value.set_halign(Gtk.Align.END)
        self.details_grid.attach(self.swap_used_value, 1, 4, 1, 1)
    
    def update_ram_bar(self, used, total, percent):
        """RAM kullanım çubuğunu günceller"""
        # Değerleri GB'a dönüştür
        used_gb = used / (1024 * 1024 * 1024)
        total_gb = total / (1024 * 1024 * 1024)
        
        # Değerleri güncelle
        self.ram_value.set_text(f"{used_gb:.1f} / {total_gb:.1f} GB ({percent:.1f}%)")
        self.ram_bar.set_fraction(percent / 100)
        
        # Renk sınıfını güncelle
        self.ram_bar.remove_css_class("low")
        self.ram_bar.remove_css_class("medium")
        self.ram_bar.remove_css_class("high")
        
        if percent < 50:
            self.ram_bar.add_css_class("low")
        elif percent < 80:
            self.ram_bar.add_css_class("medium")
        else:
            self.ram_bar.add_css_class("high")
    
    def update_swap_bar(self, used, total, percent):
        """Swap kullanım çubuğunu günceller"""
        # Değerleri GB'a dönüştür
        used_gb = used / (1024 * 1024 * 1024)
        total_gb = total / (1024 * 1024 * 1024)
        
        # Değerleri güncelle
        self.swap_value.set_text(f"{used_gb:.1f} / {total_gb:.1f} GB ({percent:.1f}%)")
        self.swap_bar.set_fraction(percent / 100)
        
        # Renk sınıfını güncelle
        self.swap_bar.remove_css_class("low")
        self.swap_bar.remove_css_class("medium")
        self.swap_bar.remove_css_class("high")
        
        if percent < 50:
            self.swap_bar.add_css_class("low")
        elif percent < 80:
            self.swap_bar.add_css_class("medium")
        else:
            self.swap_bar.add_css_class("high")
    
    def update_memory_details(self, ram_info, swap_info):
        """Detaylı bellek bilgilerini günceller"""
        # RAM değerlerini GB'a dönüştür
        total_gb = ram_info["total"] / (1024 * 1024 * 1024)
        used_gb = ram_info["used"] / (1024 * 1024 * 1024)
        free_gb = ram_info["free"] / (1024 * 1024 * 1024)
        
        # Swap değerlerini GB'a dönüştür
        swap_total_gb = swap_info["total"] / (1024 * 1024 * 1024)
        swap_used_gb = swap_info["used"] / (1024 * 1024 * 1024)
        
        # Değerleri güncelle
        self.total_value.set_text(f"{total_gb:.2f} GB")
        self.used_value.set_text(f"{used_gb:.2f} GB")
        self.free_value.set_text(f"{free_gb:.2f} GB")
        self.swap_total_value.set_text(f"{swap_total_gb:.2f} GB")
        self.swap_used_value.set_text(f"{swap_used_gb:.2f} GB")
