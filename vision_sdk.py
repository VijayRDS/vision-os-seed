#!/usr/bin/env python3
"""
Vision OS SDK (v0.2) — Lightweight App & Service Runtime
Allows users to create custom low-footprint apps and background services.
"""

import json
import os
from pathlib import Path

APPS_DIR = Path(__file__).parent / "vision_apps"
APPS_DIR.mkdir(exist_ok=True)


def create_custom_app(app_name: str, description: str, code_body: str) -> Path:
    """Generates a self-contained Vision OS micro-app inside vision_apps/."""
    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in app_name.lower())
    app_folder = APPS_DIR / safe_name
    app_folder.mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": app_name,
        "id": safe_name,
        "description": description,
        "memory_limit_mb": 32,
        "sandboxed": True
    }
    with open(app_folder / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    script_content = f'''import tkinter as tk

def run(parent_root):
    win = tk.Toplevel(parent_root)
    win.title("Vision App :: {app_name}")
    win.geometry("420x300")
    win.configure(bg="#0b1320")
{code_body}
'''
    app_file = app_folder / "app.py"
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(script_content)

    return app_file


def list_custom_apps() -> list[dict]:
    apps = []
    for folder in APPS_DIR.iterdir():
        manifest_file = folder / "manifest.json"
        if folder.is_dir() and manifest_file.exists():
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["path"] = str(folder / "app.py")
                apps.append(data)
    return apps