"""
Espresso - Disk tarama modeli
"""

import os
import threading
from pathlib import Path
from collections import defaultdict


class DiskScanner:
    """Dizin yapısını tarayıp boyut bilgilerini toplayan sınıf"""
    
    def __init__(self):
        self.results = {}
        self.stop_requested = False
        self.lock = threading.Lock()
    
    def scan_directory(self, directory):
        """Belirtilen dizini tarar ve boyut bilgilerini toplar"""
        self.stop_requested = False
        self.results = {}
        
        try:
            # Dizin yolunu normalize et
            directory = os.path.abspath(os.path.expanduser(directory))
            
            # Dizin var mı kontrol et
            if not os.path.isdir(directory):
                return
            
            # Dizini tara
            self._scan_recursive(directory)
            
            # Sonuçları düzenle
            self._organize_results()
            
        except (PermissionError, OSError) as e:
            print(f"Tarama hatası: {e}")
    
    def _scan_recursive(self, directory, depth=0, max_depth=5):
        """Dizini özyinelemeli olarak tarar"""
        # Çok derine inmeyi önle
        if depth > max_depth or self.stop_requested:
            return 0
        
        total_size = 0
        
        try:
            # Dizin içeriğini listele
            with os.scandir(directory) as entries:
                for entry in entries:
                    if self.stop_requested:
                        return 0
                    
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            # Alt dizin boyutunu hesapla
                            subdir_size = self._scan_recursive(
                                entry.path, depth + 1, max_depth
                            )
                            
                            # Sonuçlara ekle
                            with self.lock:
                                self.results[entry.path] = {
                                    "name": entry.name,
                                    "type": "directory",
                                    "size": subdir_size,
                                    "parent": directory
                                }
                            
                            total_size += subdir_size
                            
                        elif entry.is_file(follow_symlinks=False):
                            # Dosya boyutunu al
                            file_size = entry.stat().st_size
                            
                            # Sonuçlara ekle
                            with self.lock:
                                self.results[entry.path] = {
                                    "name": entry.name,
                                    "type": "file",
                                    "size": file_size,
                                    "parent": directory
                                }
                            
                            total_size += file_size
                    
                    except (PermissionError, OSError):
                        # Bazı dosya/dizinlere erişim izni olmayabilir
                        continue
        
        except (PermissionError, OSError):
            # Dizine erişim izni olmayabilir
            pass
        
        return total_size
    
    def _organize_results(self):
        """Sonuçları düzenler ve ağaç yapısı oluşturur"""
        # Sonuçları boyuta göre sırala
        sorted_results = {}
        
        # Önce dizinleri ve dosyaları ayır
        directories = {}
        files = {}
        
        for path, info in self.results.items():
            if info["type"] == "directory":
                directories[path] = info
            else:
                files[path] = info
        
        # Dizinleri boyuta göre sırala
        sorted_dirs = sorted(
            directories.items(),
            key=lambda x: x[1]["size"],
            reverse=True
        )
        
        # Dosyaları boyuta göre sırala
        sorted_files = sorted(
            files.items(),
            key=lambda x: x[1]["size"],
            reverse=True
        )
        
        # Sonuçları birleştir
        for path, info in sorted_dirs:
            sorted_results[path] = info
        
        for path, info in sorted_files:
            sorted_results[path] = info
        
        self.results = sorted_results
    
    def stop_scan(self):
        """Devam eden taramayı durdurur"""
        self.stop_requested = True
    
    def get_results(self):
        """Tarama sonuçlarını döndürür"""
        return self.results
    
    def get_directory_tree(self):
        """Sonuçları ağaç yapısında döndürür"""
        tree = defaultdict(list)
        
        for path, info in self.results.items():
            parent = info["parent"]
            tree[parent].append(path)
        
        return tree
    
    @staticmethod
    def format_size(size_bytes):
        """Bayt cinsinden boyutu insan okunabilir formata dönüştürür"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        
        size_kb = size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} KB"
        
        size_mb = size_kb / 1024
        if size_mb < 1024:
            return f"{size_mb:.2f} MB"
        
        size_gb = size_mb / 1024
        return f"{size_gb:.2f} GB"
