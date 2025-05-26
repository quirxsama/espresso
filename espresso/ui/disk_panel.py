"""
Espresso - Disk panel bileşeni
"""

import os
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio, GdkPixbuf

from espresso.models.disk_scanner import DiskScanner


class DiskPanel(Gtk.Box):
    """Disk paneli bileşeni"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # CSS sınıfı ekle
        self.add_css_class("panel")
        
        # Panel başlığı
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.append(title_box)
        
        title_label = Gtk.Label(label="Disk")
        title_label.add_css_class("panel-title")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_hexpand(True)
        title_box.append(title_label)
        
        # Tarama butonu
        self.scan_button = Gtk.Button()
        self.scan_button.set_icon_name("folder-symbolic")
        self.scan_button.set_tooltip_text("Dizin Tara")
        title_box.append(self.scan_button)
        
        # Disk kullanım bilgileri
        usage_frame = Gtk.Frame()
        usage_frame.set_margin_top(8)
        self.append(usage_frame)
        
        self.usage_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.usage_box.set_margin_top(8)
        self.usage_box.set_margin_bottom(8)
        self.usage_box.set_margin_start(8)
        self.usage_box.set_margin_end(8)
        usage_frame.set_child(self.usage_box)
        
        # Disk bölümleri için dinamik olarak oluşturulacak
        self.partition_bars = {}
        
        # Dizin tarama sonuçları
        tree_frame = Gtk.Frame()
        tree_frame.set_margin_top(16)
        tree_frame.set_vexpand(True)
        self.append(tree_frame)
        
        tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        tree_box.set_margin_top(8)
        tree_box.set_margin_bottom(8)
        tree_box.set_margin_start(8)
        tree_box.set_margin_end(8)
        tree_frame.set_child(tree_box)
        
        tree_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        tree_box.append(tree_header)
        
        tree_label = Gtk.Label(label="Dizin Tarama")
        tree_label.set_halign(Gtk.Align.START)
        tree_label.set_hexpand(True)
        tree_header.append(tree_label)
        
        self.scan_status = Gtk.Spinner()
        self.scan_status.set_visible(False)
        tree_header.append(self.scan_status)
        
        # Ağaç görünümü
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_margin_top(8)
        tree_box.append(scrolled_window)
        
        # Ağaç görünümü modeli
        self.tree_store = Gtk.TreeStore(
            str,    # Dizin/dosya adı
            str,    # Boyut (insan okunabilir)
            int,    # Boyut (bayt)
            str,    # Tür (dizin/dosya)
            str,    # Tam yol
            str     # İkon adı
        )
        
        # Ağaç görünümü
        self.tree_view = Gtk.TreeView(model=self.tree_store)
        self.tree_view.set_headers_visible(True)
        scrolled_window.set_child(self.tree_view)
        
        # İkon sütunu
        icon_renderer = Gtk.CellRendererPixbuf()
        icon_column = Gtk.TreeViewColumn("", icon_renderer, icon_name=5)
        self.tree_view.append_column(icon_column)
        
        # Ad sütunu
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn("Ad", name_renderer, text=0)
        name_column.set_expand(True)
        name_column.set_sort_column_id(0)
        self.tree_view.append_column(name_column)
        
        # Boyut sütunu
        size_renderer = Gtk.CellRendererText()
        size_renderer.set_alignment(1.0, 0.5)
        size_column = Gtk.TreeViewColumn("Boyut", size_renderer, text=1)
        size_column.set_sort_column_id(2)
        self.tree_view.append_column(size_column)
        
        # Tür sütunu
        type_renderer = Gtk.CellRendererText()
        type_column = Gtk.TreeViewColumn("Tür", type_renderer, text=3)
        type_column.set_sort_column_id(3)
        self.tree_view.append_column(type_column)
    
    def update_disk_usage(self, disk_info):
        """Disk kullanım bilgilerini günceller"""
        # Önce mevcut bileşenleri temizle
        while child := self.usage_box.get_first_child():
            self.usage_box.remove(child)
        
        self.partition_bars = {}
        
        # Her disk bölümü için kullanım çubuğu ekle
        for mount_point, info in disk_info.items():
            # Bazı özel bölümleri atla
            if mount_point in ["/dev", "/sys", "/proc", "/run"]:
                continue
            
            # Bölüm kutusu
            partition_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            partition_box.set_margin_top(8)
            self.usage_box.append(partition_box)
            
            # Bölüm etiketi
            label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            partition_box.append(label_box)
            
            # Bölüm adı
            name = mount_point
            if mount_point == "/":
                name = "/ (Kök)"
            elif mount_point == "/home":
                name = "/home (Ev)"
            
            partition_label = Gtk.Label(label=f"{name}:")
            partition_label.set_halign(Gtk.Align.START)
            label_box.append(partition_label)
            
            # Kullanım bilgisi
            total_gb = info["total"] / (1024 * 1024 * 1024)
            used_gb = info["used"] / (1024 * 1024 * 1024)
            percent = info["percent"]
            
            usage_label = Gtk.Label(label=f"{used_gb:.1f} / {total_gb:.1f} GB ({percent:.1f}%)")
            usage_label.set_halign(Gtk.Align.END)
            usage_label.set_hexpand(True)
            label_box.append(usage_label)
            
            # İlerleme çubuğu
            progress_bar = Gtk.ProgressBar()
            progress_bar.set_fraction(percent / 100)
            progress_bar.add_css_class("usage-bar")
            
            # Renk sınıfını ayarla
            if percent < 70:
                progress_bar.add_css_class("low")
            elif percent < 90:
                progress_bar.add_css_class("medium")
            else:
                progress_bar.add_css_class("high")
            
            partition_box.append(progress_bar)
            
            # Çubuğu sözlüğe ekle
            self.partition_bars[mount_point] = {
                "bar": progress_bar,
                "label": usage_label
            }
    
    def update_scan_status(self, scanning):
        """Tarama durumunu günceller"""
        if scanning:
            self.scan_status.set_visible(True)
            self.scan_status.start()
        else:
            self.scan_status.stop()
            self.scan_status.set_visible(False)
    
    def update_directory_tree(self, scan_results):
        """Dizin ağacını günceller"""
        # Ağaç modelini temizle
        self.tree_store.clear()
        
        # Kök dizinleri bul
        root_paths = set()
        for path, info in scan_results.items():
            parent = info["parent"]
            if parent not in scan_results:
                root_paths.add(parent)
        
        # Her kök dizin için ağaç oluştur
        for root_path in sorted(root_paths):
            self._add_directory_to_tree(None, root_path, scan_results)
    
    def _add_directory_to_tree(self, parent_iter, directory, scan_results):
        """Dizini ve alt öğelerini ağaca ekler"""
        # Dizin adını al
        dir_name = os.path.basename(directory)
        if not dir_name:  # Kök dizin için
            dir_name = directory
        
        # Dizin bilgilerini al
        dir_info = scan_results.get(directory)
        if dir_info:
            dir_size = dir_info["size"]
            dir_size_str = DiskScanner.format_size(dir_size)
            dir_type = "Dizin"
            dir_icon = "folder-symbolic"
        else:
            dir_size = 0
            dir_size_str = "0 B"
            dir_type = "Dizin"
            dir_icon = "folder-symbolic"
        
        # Dizini ağaca ekle
        dir_iter = self.tree_store.append(parent_iter, [
            dir_name, dir_size_str, dir_size, dir_type, directory, dir_icon
        ])
        
        # Alt öğeleri bul
        children = {}
        for path, info in scan_results.items():
            if info["parent"] == directory:
                children[path] = info
        
        # Önce dizinleri ekle
        for path, info in sorted(children.items(), key=lambda x: x[0]):
            if info["type"] == "directory":
                self._add_directory_to_tree(dir_iter, path, scan_results)
        
        # Sonra dosyaları ekle
        for path, info in sorted(children.items(), key=lambda x: x[0]):
            if info["type"] == "file":
                file_name = info["name"]
                file_size = info["size"]
                file_size_str = DiskScanner.format_size(file_size)
                
                # Dosya türüne göre ikon belirle
                file_icon = "text-x-generic-symbolic"
                
                # Uzantıya göre ikon
                if file_name.endswith((".jpg", ".jpeg", ".png", ".gif")):
                    file_icon = "image-x-generic-symbolic"
                elif file_name.endswith((".mp3", ".wav", ".ogg", ".flac")):
                    file_icon = "audio-x-generic-symbolic"
                elif file_name.endswith((".mp4", ".mkv", ".avi", ".mov")):
                    file_icon = "video-x-generic-symbolic"
                elif file_name.endswith((".pdf", ".epub")):
                    file_icon = "x-office-document-symbolic"
                elif file_name.endswith((".zip", ".tar", ".gz", ".xz", ".bz2")):
                    file_icon = "package-x-generic-symbolic"
                
                # Dosyayı ağaca ekle
                self.tree_store.append(dir_iter, [
                    file_name, file_size_str, file_size, "Dosya", path, file_icon
                ])
