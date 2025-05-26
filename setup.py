#!/usr/bin/env python3
"""
Espresso - Sistem Monitörü kurulum betiği
"""

import os
from setuptools import setup, find_packages

# Desktop girişi dosyası
desktop_entry = """[Desktop Entry]
Name=Espresso
Comment=Gerçek Zamanlı Sistem Monitörü
Exec=espresso
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=System;Monitor;
Keywords=System;Monitor;CPU;RAM;GPU;Disk;
"""

# Kurulum sonrası betik
def post_install():
    """Kurulum sonrası işlemler"""
    # Desktop girişi oluştur
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    
    with open(os.path.join(desktop_dir, "espresso.desktop"), "w") as f:
        f.write(desktop_entry)
    
    print("Desktop girişi oluşturuldu: ~/.local/share/applications/espresso.desktop")

# Kurulum
setup(
    name="espresso",
    version="0.1.0",
    description="Gerçek Zamanlı Sistem Monitörü",
    author="Espresso Takımı",
    author_email="kaanyokuss76@gmail.com",
    url="https://github.com/quirxsama/espresso",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "espresso=espresso.__main__:main",
        ],
    },
    install_requires=[
        "psutil>=5.9.0",
        "pynvml>=11.0.0",
        "PyGObject>=3.42.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Monitoring",
    ],
)

# Kurulum sonrası işlemleri çalıştır
if __name__ == "__main__":
    post_install()
