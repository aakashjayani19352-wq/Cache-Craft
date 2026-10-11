"""
device_auth.py — Hardware and Device Authorization for Cache-Craft
Ensures local GPU (NVIDIA RTX 4060) and Ollama resources are only accessible
on the creator's physical laptop (HP-OMEN-16).
Friends and remote/guest clients are restricted to Online Cloud mode.
"""

import os
import platform

# Creator's authorized machine identifiers
CREATOR_MACHINE_NAMES = {"HP-OMEN-16"}
CREATOR_USERNAMES = {"123"}


def is_creator_hardware() -> bool:
    """
    Checks whether the current server is executing on the creator's physical HP Omen laptop.
    """
    node_name = platform.node().upper()
    comp_name = os.environ.get("COMPUTERNAME", "").upper()
    user_name = os.environ.get("USERNAME", "")
    creator_flag = os.environ.get("CREATOR_DEVICE", "").lower() in ("true", "1", "yes")

    if creator_flag:
        return True

    if node_name in CREATOR_MACHINE_NAMES or comp_name in CREATOR_MACHINE_NAMES:
        return True

    if user_name in CREATOR_USERNAMES and ("OMEN" in node_name or "OMEN" in comp_name):
        return True

    return False


def is_gpu_access_authorized(client_ip: str | None = None) -> bool:
    """
    Returns True ONLY if:
    1. The server is physically running on the creator's laptop (HP-OMEN-16).
    2. The client making the request is local loopback (127.0.0.1, ::1, localhost, testclient).
    If a friend is testing from another PC or across LAN/network, returns False.
    """
    if not is_creator_hardware():
        return False

    if client_ip:
        ip = client_ip.strip()
        # Loopback addresses
        if ip not in ("127.0.0.1", "::1", "localhost", "testclient"):
            return False

    return True
