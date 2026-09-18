"""
MODULI I SIGURISË DHE AUTORIZIMIT PËR STRICT LOUNGE & BAR
Mbron seksionet e ndjeshme (Menyja, Çmimet, Raportet Financiare) me Kodin e Sigurisë.
"""

import hmac
import hashlib
import time
from typing import Optional
from core.config import PIN_SHA256_HASH, SECRET_KEY

AUTH_COOKIE_NAME = "strict_admin_token"
SESSION_MAX_AGE_SECONDS = 12 * 3600  # 12 orë e vlefshme


def verify_pin(input_pin: str) -> bool:
    """Verifikon nëse kodi i dhënë përputhet me kodin zyrtar të sigurisë pa ekspozuar kodin."""
    if not input_pin:
        return False
    pin_clean = input_pin.strip()
    hashed = hashlib.sha256(pin_clean.encode("utf-8")).hexdigest()
    return hmac.compare_digest(hashed, PIN_SHA256_HASH)


def generate_auth_token() -> str:
    """Gjeneron një token të nënshkruar kriptografikisht për sesionin e autorizuar."""
    timestamp = str(int(time.time()))
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        timestamp.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{timestamp}.{signature}"


def is_authenticated_token(token: Optional[str]) -> bool:
    """Verifikon vlefshmërinë e tokenit të autorizimit."""
    if not token or "." not in token:
        return False

    try:
        parts = token.split(".", 1)
        timestamp_str, signature = parts[0], parts[1]
        timestamp = int(timestamp_str)

        # Kontrollojmë kohën e skadimit (12 orë)
        if time.time() - timestamp > SESSION_MAX_AGE_SECONDS:
            return False

        # Verifikojmë nënshkrimin
        expected_sig = hmac.new(
            SECRET_KEY.encode("utf-8"),
            timestamp_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_sig)
    except Exception:
        return False
