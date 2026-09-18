"""
Nis vetëm Serverin Web të Restaurantit (FastAPI + Uvicorn).
I përshtatshëm për server qendror ose pajisje që përdorin vetëm shfletuesin (Tableta, Smartphone, KDS).
"""

import uvicorn
import webbrowser
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.config import WEB_HOST, WEB_PORT, get_local_ip, RESTAURANT_NAME


def run_web():
    local_ip = get_local_ip()
    print("=" * 60)
    print(f" {RESTAURANT_NAME} - SERVERI WEB PO NIS...")
    print("=" * 60)
    print(f"• Adresa Lokale (ky kompjuter): http://localhost:{WEB_PORT}")
    print(f"• Adresa në Rrjet (Telefon/Tablet/Kuzhinë): http://{local_ip}:{WEB_PORT}")
    print("=" * 60)
    print("Faqet në dispozicion:")
    print(f"  1. Kasa POS (Kamarierët):  http://localhost:{WEB_PORT}/pos")
    print(f"  2. Ekrani i Kuzhinës (KDS): http://localhost:{WEB_PORT}/kitchen")
    print(f"  3. Harta e Tavolinave:     http://localhost:{WEB_PORT}/tables")
    print(f"  4. Menaxhimi i Menysë:     http://localhost:{WEB_PORT}/admin/menu")
    print(f"  5. Raportet & Statistikat: http://localhost:{WEB_PORT}/reports")
    print("=" * 60)

    # Hapim shfletuesin automatikisht nëse nuk kalohet flamuri --no-browser
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(f"http://localhost:{WEB_PORT}")
        except Exception:
            pass

    uvicorn.run("web.app:app", host=WEB_HOST, port=WEB_PORT, reload=False)


if __name__ == "__main__":
    run_web()
