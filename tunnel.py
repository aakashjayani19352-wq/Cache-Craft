"""
tunnel.py — CLI to Start, Stop, or Check Cloudflare Tunnel for Cache-Craft
Usage:
  python tunnel.py start
  python tunnel.py stop
  python tunnel.py status
"""

import sys
import json
from core.tunnel_manager import start_tunnel, stop_tunnel, get_tunnel_status


def main():
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()

    if cmd == "start":
        print("Starting Cloudflare Tunnel for Cache-Craft RTX 4060 GPU...")
        res = start_tunnel()
        if res.get("status") == "active":
            print("\n============================================================")
            print("⚡ CLOUDFLARE TUNNEL ONLINE!")
            print(f"👉 Public URL:  {res['url']}")
            print(f"🎯 Target:      {res['target']}")
            print(f"💻 Device:      {res['device']}")
            print("============================================================\n")
            print("Anyone visiting cache-craft.vercel.app can now route offline")
            print("queries to your physical laptop RTX 4060 GPU!")
            print("Run 'python tunnel.py stop' anytime to disable remote access.\n")
        else:
            print("Failed to start tunnel:", res.get("message"))

    elif cmd == "stop":
        print("Stopping Cloudflare Tunnel...")
        res = stop_tunnel()
        print("Status:", res.get("message", "Stopped"))

    elif cmd in ("status", "check"):
        res = get_tunnel_status()
        print("\n============================================================")
        print(f"Cloudflare Tunnel Status: {res['status'].upper()}")
        if res.get("url"):
            print(f"Live URL: {res['url']}")
        print(f"Hardware: {res['device']}")
        print("============================================================\n")

    else:
        print("Usage: python tunnel.py [start | stop | status]")


if __name__ == "__main__":
    main()
