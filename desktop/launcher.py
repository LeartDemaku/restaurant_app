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


def ensure_server_running(max_wait_seconds: float = 5.0) -> bool:
    """Siguron që serveri ueb është duke punuar; nëse jo, e nis në sfond."""
    seed_database()

    if is_server_alive():
        return True

    # Nisim serverin në një daemon thread
    server_thread = threading.Thread(target=_run_uvicorn_server, daemon=True)
    server_thread.start()

    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        if is_server_alive():
            return True
        time.sleep(0.15)

    return is_server_alive()


def get_desktop_app_command(url: str) -> Optional[List[str]]:
    """
    Gjen rrugën e Microsoft Edge ose Google Chrome për të hapur dritaren
    në mënyrën 'App' (pa shirit kërkimi, pa tabs, si aplikacion i mirëfilltë desktop).
    """
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
                "--new-window",
                "--window-size=1440,900"
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
                "--new-window",
                "--window-size=1440,900"
            ]

    return None


def launch_desktop(target_url: Optional[str] = None):
    """
    Nis aplikacionin desktop:
    1. Siguron që serveri është aktiv.
    2. Hap dritaren e aplikacionit 100% identike me uebin.
    3. Mban procesin aktiv derisa përdoruesi të mbyllë dritaren.
    """
    ensure_server_running()

    url = target_url or f"http://127.0.0.1:{WEB_PORT}"
    cmd = get_desktop_app_command(url)

    if cmd:
        try:
            # Nisim dritaren si proces të pavarur dhe presim derisa të mbyllet
            proc = subprocess.Popen(cmd)
            proc.wait()
            return
        except Exception:
            pass

    # Fallback në rast të jashtëzakonshëm: hapim në shfletuesin e sistemit
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    launch_desktop()
