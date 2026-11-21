#!/usr/bin/env python3
"""
Vision OS - Adaptive Runtime & Mode-Selectable Launcher (Seed v0.1)
Demonstrates intent-driven resource allocation and telemetry feedback.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
PROFILES_PATH = BASE_DIR / "profiles.json"
TELEMETRY_LOG = BASE_DIR / "vision_telemetry.jsonl"


def load_profiles() -> dict:
    with open(PROFILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_browser() -> str | None:
    candidates = [
        "google-chrome",
        "chromium",
        "chromium-browser",
        "brave-browser",
        "microsoft-edge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if shutil.which(candidate) or os.path.exists(candidate):
            return candidate
    return None


def log_telemetry(profile_key: str, duration_sec: float, exit_code: int) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "profile": profile_key,
        "session_duration_sec": round(duration_sec, 2),
        "exit_code": exit_code,
    }
    with open(TELEMETRY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def launch_profile(profile_key: str, profile: dict, url: str) -> None:
    browser = detect_browser()
    if not browser:
        print("[Vision Error] No Chromium-based browser binary found on PATH.")
        sys.exit(1)

    user_data_dir = BASE_DIR / ".vision_runtime" / profile_key
    user_data_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        browser,
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        *profile["flags"],
        url,
    ]

    print(f"\n[Vision Kernel] Initializing '{profile['name']}'")
    print(f"[Vision Kernel] Memory Budget: {profile['max_memory_mb']} MB | GPU: {profile['gpu_acceleration']}")
    print(f"[Vision Kernel] Launching isolated runtime...\n")

    start = time.time()
    proc = subprocess.run(cmd)
    elapsed = time.time() - start

    log_telemetry(profile_key, elapsed, proc.returncode)
    print(f"\n[Vision Telemetry] Session logged ({elapsed:.1f}s). Ready for profile adaptation.")


def main() -> None:
    profiles = load_profiles()
    print("=== VISION OS :: ADAPTIVE EXECUTION LAYER (v0.1) ===")
    keys = list(profiles.keys())

    for idx, key in enumerate(keys, start=1):
        p = profiles[key]
        print(f"  {idx}. [{key.upper()}] {p['name']} — {p['description']}")

    choice = input("\nSelect execution mode (1-3): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
        print("Invalid selection.")
        sys.exit(1)

    selected_key = keys[int(choice) - 1]
    target_url = input("Enter URL (press Enter for default): ").strip() or "https://example.com"
    launch_profile(selected_key, profiles[selected_key], target_url)


if __name__ == "__main__":
    main()