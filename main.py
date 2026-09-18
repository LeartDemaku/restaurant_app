"""
PIKA QENDRORE E HYRJES PËR SISTEMIN E RESTAURANTIT
Mundëson:
1. Nisjen e dyfishtë (Desktop GUI + Web Server në sfond) - PARAZGJEDHUR
2. Nisjen vetëm të Web Serverit (--web)
3. Nisjen vetëm të Desktop App (--desktop)
"""

import sys
import threading
import time
import uvicorn
import qrcode

# Sigurojmë kodim UTF-8 në Windows terminal
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.config import WEB_HOST, WEB_PORT, get_local_ip, RESTAURANT_NAME
from desktop.app_gui import RestaurantAppGUI
from database.seed_data import seed_database


def run_web_server():
    """Funksion që ekzekutohet në një thread në sfond për të shërbyer uebin."""
    config = uvicorn.Config("web.app:app", host=WEB_HOST, port=WEB_PORT, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def print_banner_and_qr():
    """Shfaq lidhjet dhe QR code në terminal për lidhjen e telefonave të stafit."""
    local_ip = get_local_ip()
    web_url = f"http://{local_ip}:{WEB_PORT}"

    print("=" * 65)
    print(f"       🍽️  {RESTAURANT_NAME}  🍽️")
    print("   SISTEMI I INTEGRUAR I MENAXHIMIT TË RESTAURANTIT")
    print("=" * 65)
    print(f"• Desktop App:          Duke u hapur në ekran...")
    print(f"• Web Serveri Lokalisht: http://localhost:{WEB_PORT}")
    print(f"• Qasja nga Telefonat:   {web_url}")
    print("=" * 65)

    try:
        # Gjenerojmë një QR kod tekstual në terminal për skanim të shpejtë
        qr = qrcode.QRCode(version=1, box_size=1, border=1)
        qr.add_data(web_url)
        qr.make(fit=True)
        print("\nSkanoni këtë QR Code me telefon për të hapur POS-in e kamarierëve:")
        qr.print_ascii(invert=True)
    except Exception:
        pass
    print("=" * 65)


def main():
    # Inicializimi i bazës së të dhënave dhe artikujve
    seed_database()

    args = sys.argv[1:]

    if "--web" in args or "--web-only" in args:
        print_banner_and_qr()
        uvicorn.run("web.app:app", host=WEB_HOST, port=WEB_PORT, reload=False)

    elif "--desktop" in args or "--desktop-only" in args:
        print(f"Duke nisur vetëm Desktop GUI për {RESTAURANT_NAME}...")
        gui = RestaurantAppGUI()
        gui.mainloop()

    else:
        # Mënyra e Integruar (Desktop App + Web Server paralel)
        print_banner_and_qr()

        # Nisim serverin ueb në një thread të pavarur (daemon thread)
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()

        time.sleep(0.6)  # Presim një moment që uvicorn të jetë gati

        # Nisim aplikacionin Desktop në thread-in kryesor
        gui = RestaurantAppGUI()
        gui.mainloop()


if __name__ == "__main__":
    main()
