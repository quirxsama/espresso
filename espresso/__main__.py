#!/usr/bin/env python3
"""
Espresso - Ana uygulama başlatıcı
"""

import sys
import argparse
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from espresso.controllers.app_controller import AppController


def parse_arguments():
    """Komut satırı argümanlarını işler"""
    parser = argparse.ArgumentParser(description="Espresso Sistem Monitörü")
    parser.add_argument("--interval", type=int, default=1,
                        help="Veri güncelleme aralığı (saniye)")
    parser.add_argument("--theme", type=str, choices=["light", "dark"], default="dark",
                        help="Uygulama teması (açık/koyu)")
    parser.add_argument("--scan-home", action="store_true",
                        help="Home dizinini otomatik tara")
    return parser.parse_args()


def main():
    """Ana uygulama başlatıcı"""
    args = parse_arguments()
    
    # Uygulama kontrolcüsünü başlat
    app_controller = AppController(
        update_interval=args.interval,
        theme=args.theme,
        scan_home=args.scan_home
    )
    
    # GTK uygulamasını çalıştır
    app = app_controller.get_app()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
