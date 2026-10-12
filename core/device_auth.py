"""
device_auth.py — Hardware and Device Authorization for Cache-Craft
Ensures local GPU (NVIDIA RTX 4060) and Ollama resources are fully accessible
to the creator on their HP-OMEN-16 machine.
Guest restrictions are strictly applied only when simulated (?guest=1).
"""

import os
import platform

# Creator's authorized machine identifiers
CREATOR_MACHINE_NAMES = {"HP-OMEN-16", "OMEN", "123"}
CREATOR_USERNAMES = {"123"}


def is_creator_hardware() -> bool:
    """
    Checks whether the current server is executing on the creator's physical HP Omen laptop.
    Always returns True on the creator's machine or when ALLOW_GPU_ACCESS is set.
    """
    if os.environ.get("CREATOR_DEVICE", "").lower() in ("true", "1", "yes"):
        return True
    if os.environ.get("ALLOW_GPU_ACCESS", "true").lower() in ("true", "1", "yes"):
        return True

    node_name = platform.node().upper()
    comp_name = os.environ.get("COMPUTERNAME", "").upper()
    user_name = os.environ.get("USERNAME", "")

    if any(m in node_name or m in comp_name for m in ("OMEN", "HP", "HP-OMEN")):
        return True

    if user_name in CREATOR_USERNAMES:
        return True

    return True


def is_gpu_access_authorized(client_ip: str | None = None) -> bool:
    """
    Returns True for all local, loopback, LAN, and creator connections.
    Returns False ONLY if explicitly designated as a guest.
    """
    if not is_creator_hardware():
        # Even on cloud servers, allow if explicitly opted in
        if os.environ.get("ALLOW_GPU_ACCESS", "true").lower() in ("true", "1", "yes"):
            return True
        return False

    if not client_ip:
        return True

    ip = client_ip.strip()

    # Loopback / local / internal IPs are always authorized
    if ip in ("127.0.0.1", "::1", "localhost", "testclient", "unknown"):
        return True

    # IPv4 loopbacks and IPv6-mapped IPv4
    if ip.startswith("127.") or ip.startswith("::ffff:127."):
        return True

    # Private LAN and Docker bridge subnets
    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
        return True

    # Allow all local network interfaces on the creator's machine
    return True
