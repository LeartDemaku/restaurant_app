import socket
from pathlib import Path

# Konfigurimet kryesore të restaurantit
APP_NAME = "Sistemi i Menaxhimit të Restaurantit"
RESTAURANT_NAME = "STRICT LOUNGE & BAR"
RESTAURANT_ADDRESS = "Rruga Kryesore, Prishtinë"
RESTAURANT_PHONE = "+383 44 123 456"
CURRENCY = "€"

import os
from dotenv import load_dotenv

# Ngarkojmë konfigurimet sekrete nga .env
load_dotenv()

# Konfigurimet e Sigurisë (Kodi verifikohet me Hash SHA-256 pa u ekspozuar asnjëherë)
PIN_SHA256_HASH = "b90e97f4eae90b89fae27840e851ea9802d84f8d512a58bf5460f926b5ab4717"
SECRET_KEY = "strict_lounge_bar_super_secret_pin_key_2026"

# Konfigurimet e Serverit
WEB_HOST = "0.0.0.0"
WEB_PORT = 8000

# Rrugët
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "restaurant.db"


def get_local_ip() -> str:
    """Gjen IP adresën lokale të kompjuterit në rrjetin Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_web_url() -> str:
    """Kthen URL-në lokale të serverit ueb."""
    return f"http://{get_local_ip()}:{WEB_PORT}"
