"""
LAUNCHER I APLIKACIONIT DESKTOP - STRICT LOUNGE & BAR
Mundëson hapjen e aplikacionit në një dritare të pavarur desktop (App Mode),
duke garantuar që paraqitja vizuale dhe funksionet të jenë 100% identike me uebin.
"""

import os
import sys
import time
import socket
import subprocess
import threading
import webbrowser
from typing import Optional, List

from core.config import WEB_HOST, WEB_PORT, RESTAURANT_NAME
from database.seed_data import seed_database


def is_server_alive(host: str = "127.0.0.1", port: int = WEB_PORT, timeout: float = 0.3) -> bool:
    """Kontrollon nëse serveri ueb është tashmë aktiv në portën e caktuar."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def _run_uvicorn_server():
    """Nis uvicorn serverin për backend-in ueb."""
    import uvicorn
    config = uvicorn.Config("web.app:app", host=WEB_HOST, port=WEB_PORT, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def ensure_server_running(max_wait_seconds: float = 20.0) -> bool:
    """Siguron që serveri ueb është duke punuar; nëse jo, e nis në sfond."""
    seed_database()

    if is_server_alive():
        return True

    # Nisim serverin në një daemon thread
    server_thread = threading.Thread(target=_run_uvicorn_server, daemon=True)
    server_thread.start()

    start_time = time.time()
    dots = 0
    while time.time() - start_time < max_wait_seconds:
        if is_server_alive():
            print(f"\n✅ Serveri u nis me sukses!")
            return True
        dots += 1
        if dots % 7 == 0:
            elapsed = int(time.time() - start_time)
            print(f"   Duke pritur serverin... ({elapsed}s)")
        time.sleep(0.2)

    alive = is_server_alive()
    if not alive:
        print("⚠️  Serveri nuk u nis brenda 20 sekondave. Duke provuar gjithsesi...")
    return alive


def get_desktop_app_command(url: str) -> Optional[List[str]]:
    """
    Gjen rrugën e Microsoft Edge ose Google Chrome për të hapur dritaren
    në mënyrën 'App' (pa shirit kërkimi, pa tabs, si aplikacion i mirëfilltë desktop).
    """
    # Profil i izoluar - shmang konflikte me Edge/Chrome ekzistuese
    profile_dir = os.path.join(os.path.expandvars("%APPDATA%"), "StrictLoungeBar_EdgeProfile")

    # 1. Kandidatët për Microsoft Edge (i integruar në Windows 10 & 11)
    edge_candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in edge_candidates:
        if os.path.isfile(p):
            return [
                p,
                f"--app={url}",
                f"--user-data-dir={profile_dir}",
                "--window-size=1440,900",
                "--no-first-run",
                "--no-default-browser-check",
            ]

    # 2. Kandidatët për Google Chrome
    chrome_candidates = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in chrome_candidates:
        if os.path.isfile(p):
            return [
                p,
                f"--app={url}",
                f"--user-data-dir={profile_dir}",
                "--window-size=1440,900",
                "--no-first-run",
            ]

    return None


def launch_desktop(target_url: Optional[str] = None):
    """
    Nis aplikacionin desktop:
    1. Siguron që serveri është aktiv.
    2. Hap dritaren e aplikacionit si app të pavarur.
    3. Mban serverin aktiv me loop deri sa ta ndalë përdoruesi.
    """
    alive = ensure_server_running()

    if not alive:
        print("❌ GABIM: Serveri nuk u nis. Kontrolloni requirements.txt")
        input("Shtypni Enter për të dalë...")
        return

    url = target_url or f"http://127.0.0.1:{WEB_PORT}"
    cmd = get_desktop_app_command(url)

    print(f"🚀 Duke hapur {RESTAURANT_NAME}...")

    if cmd:
        try:
            # Hap Edge/Chrome dhe MOS prit - kjo zgjidh bug-un me Edge multi-process
            subprocess.Popen(cmd)
        except Exception as e:
            print(f"⚠️  Edge/Chrome nuk u hap ({e}), duke u hapur në shfletues...")
            webbrowser.open(url)
    else:
        # Fallback: shfletues i sistemit
        webbrowser.open(url)

    print(f"✅ App është aktiv: {url}")
    print("   (Mbylleni këtë dritare ose shtypni Ctrl+C për të ndalur serverin)")

    # ─── Loop kryesor: mban serverin gjallë pa limit kohor ───────────────
    # KRITIKE: pa këtë loop, thread-i daemon (uvicorn) vdes kur Python del!
    try:
        while True:
            time.sleep(5)
            # Nëse serveri bie papritur, rinisim automatikisht
            if not is_server_alive():
                print("⚠️  Serveri u ndal papritur. Duke u rinis...")
                ensure_server_running(max_wait_seconds=15.0)
    except KeyboardInterrupt:
        print(f"\n👋 {RESTAURANT_NAME} u mbyll.")
        sys.exit(0)


if __name__ == "__main__":
    launch_desktop()
