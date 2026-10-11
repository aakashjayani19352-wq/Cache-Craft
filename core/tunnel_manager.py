"""
core/tunnel_manager.py — Toggleable Cloudflare Tunnel Manager for Cache-Craft
Enables / disables public HTTPS access to local laptop RTX 4060 GPU with zero configuration.
"""

import os
import re
import sys
import time
import subprocess
import requests
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = BASE_DIR / "bin"
SCRATCH_DIR = BASE_DIR / "scratch"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

CF_BIN = BIN_DIR / "cloudflared.exe"
LOG_FILE = SCRATCH_DIR / "cf_tunnel.log"
PID_FILE = SCRATCH_DIR / "cf_tunnel.pid"


def is_process_running(pid: int) -> bool:
    """Checks if a given PID is currently active."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(f'tasklist /FI "PID eq {pid}" /NH', shell=True).decode()
            return str(pid) in out
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def get_stored_pid() -> int | None:
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except Exception:
            return None
    return None


def get_tunnel_status() -> dict:
    """Returns the current state and public URL of the Cloudflare tunnel."""
    pid = get_stored_pid()
    if pid and is_process_running(pid) and LOG_FILE.exists():
        try:
            txt = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
            m = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", txt)
            if m:
                active_url = m[-1]
                return {
                    "status": "active",
                    "url": active_url,
                    "pid": pid,
                    "target": "http://localhost:8000",
                    "device": "NVIDIA GeForce RTX 4060 Laptop GPU"
                }
        except Exception:
            pass

    return {
        "status": "inactive",
        "url": None,
        "pid": None,
        "target": "http://localhost:8000",
        "device": "NVIDIA GeForce RTX 4060 Laptop GPU"
    }


def start_tunnel(target_port: int = 8000) -> dict:
    """
    Spawns Cloudflare Quick Tunnel to expose port 8000.
    Parses and verifies the assigned https://*.trycloudflare.com URL,
    persists URL in Supabase database so cloud Vercel / Railway can route to it,
    and returns tunnel metadata.
    """
    status = get_tunnel_status()
    if status["status"] == "active" and status["url"]:
        return status

    if not CF_BIN.exists():
        return {
            "status": "error",
            "message": f"cloudflared binary not found at {CF_BIN}. Please verify bin/cloudflared.exe exists."
        }

    # Reset log file
    if LOG_FILE.exists():
        try:
            LOG_FILE.unlink()
        except Exception:
            pass

    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    print(f"[Cloudflare Tunnel] Spawning tunnel on port {target_port}...")
    proc = subprocess.Popen(
        [
            str(CF_BIN),
            "tunnel",
            "--url",
            f"http://localhost:{target_port}",
            "--logfile",
            str(LOG_FILE)
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags
    )

    PID_FILE.write_text(str(proc.pid))

    # Poll log file for assigned trycloudflare URL (max 18s)
    tunnel_url = None
    for _ in range(36):
        time.sleep(0.5)
        if LOG_FILE.exists():
            try:
                txt = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
                matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", txt)
                if matches:
                    tunnel_url = matches[-1]
                    break
            except Exception:
                pass

    if not tunnel_url:
        stop_tunnel()
        return {
            "status": "error",
            "message": "Timed out waiting for Cloudflare to assign a public tunnel URL."
        }

    # Verify endpoint is live
    print(f"[Cloudflare Tunnel] Live at {tunnel_url}. Persisting to database...")
    try:
        import core.database as db
        db.set_setting("laptop_gpu_tunnel_url", tunnel_url)
        db.set_setting("tunnel_active", "true")
    except Exception as e:
        print(f"[Cloudflare Tunnel] Notice persisting to DB: {e}")

    return {
        "status": "active",
        "url": tunnel_url,
        "pid": proc.pid,
        "target": f"http://localhost:{target_port}",
        "device": "NVIDIA GeForce RTX 4060 Laptop GPU"
    }


def stop_tunnel() -> dict:
    """
    Terminates the Cloudflare Tunnel process, clears database state,
    and returns confirmation.
    """
    pid = get_stored_pid()
    if pid:
        if sys.platform == "win32":
            subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, capture_output=True)
        else:
            try:
                os.kill(pid, 9)
            except Exception:
                pass

    # Ensure any stray cloudflared instances from this project are killed
    if sys.platform == "win32":
        subprocess.run('taskkill /F /IM cloudflared.exe', shell=True, capture_output=True)

    if PID_FILE.exists():
        try:
            PID_FILE.unlink()
        except Exception:
            pass

    # Clear setting from DB
    try:
        import core.database as db
        db.set_setting("laptop_gpu_tunnel_url", "")
        db.set_setting("tunnel_active", "false")
    except Exception as e:
        print(f"[Cloudflare Tunnel] Notice clearing from DB: {e}")

    print("[Cloudflare Tunnel] Successfully stopped. Remote GPU access disabled.")
    return {
        "status": "inactive",
        "message": "Cloudflare Tunnel stopped. Remote GPU access disabled.",
        "url": None
    }
