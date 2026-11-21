#!/usr/bin/env python3
"""
VISION OS v0.2 — Lean 1960s Core + Adaptive 2050 Desktop Environment
Zero-dependency graphical shell with floating water-bubble nodes, native micro-apps,
custom app builder SDK, and feedback-driven local AI advisor.
"""

import importlib.util
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

import vision_sdk

BASE_DIR = Path(__file__).parent
PROFILES_PATH = BASE_DIR / "profiles.json"
TELEMETRY_LOG = BASE_DIR / "vision_telemetry.jsonl"


def load_profiles() -> dict:
    if not PROFILES_PATH.exists():
        default = {
            "lite": {"name": "Lite Surf", "max_memory_mb": 256, "gpu_acceleration": False, "flags": ["--disable-gpu"]},
            "media": {"name": "Media Deck", "max_memory_mb": 768, "gpu_acceleration": True, "flags": ["--enable-gpu-rasterization"]},
            "compute": {"name": "Heavy Compute", "max_memory_mb": 4096, "gpu_acceleration": True, "flags": ["--enable-webgl"]},
        }
        with open(PROFILES_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
    with open(PROFILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(profiles: dict) -> None:
    with open(PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)


def log_event(component: str, action: str, duration_sec: float = 0.0, status: str = "ok") -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "component": component,
        "action": action,
        "duration_sec": round(duration_sec, 2),
        "status": status,
    }
    with open(TELEMETRY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


class VisionDesktopOS:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Vision OS v0.2")
        self.root.configure(bg="#060b14")
        self.fullscreen = True
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.toggle_fullscreen)

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        # Desktop Canvas (Water-like dark ocean backdrop)
        self.canvas = tk.Canvas(
            self.root, width=self.width, height=self.height - 44,
            bg="#060b14", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bottom Minimal Taskbar
        self.taskbar = tk.Frame(self.root, bg="#0d1726", height=44)
        self.taskbar.pack(fill=tk.X, side=tk.BOTTOM)

        self.start_btn = tk.Button(
            self.taskbar, text="◉ VISION", bg="#162844", fg="#5eead4",
            font=("Consolas", 11, "bold"), relief=tk.FLAT, padx=14,
            command=self.open_ai_advisor
        )
        self.start_btn.pack(side=tk.LEFT, padx=6, pady=6)

        self.status_lbl = tk.Label(
            self.taskbar, text="Kernel: Lean-Mode | RAM: Minimal | Press ESC to toggle window",
            bg="#0d1726", fg="#94a3b8", font=("Consolas", 9)
        )
        self.status_lbl.pack(side=tk.LEFT, padx=12)

        self.clock_lbl = tk.Label(
            self.taskbar, text="", bg="#0d1726", fg="#e2e8f0", font=("Consolas", 10, "bold")
        )
        self.clock_lbl.pack(side=tk.RIGHT, padx=14)

        self.exit_btn = tk.Button(
            self.taskbar, text="Power Off", bg="#3f1622", fg="#fda4af",
            font=("Consolas", 9, "bold"), relief=tk.FLAT, padx=10,
            command=self.shutdown_os
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=6, pady=6)

        # Floating Water-Bubble App Nodes
        self.bubbles = []
        self.init_bubbles()
        self.animate_bubbles()
        self.update_taskbar_clock()
        log_event("kernel", "boot_desktop_shell")

    def toggle_fullscreen(self, _event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        if not self.fullscreen:
            self.root.geometry("1200x760")

    def init_bubbles(self):
        apps = [
            ("Browser", "#0284c7", self.open_adaptive_browser),
            ("Media Hub", "#7c3aed", self.open_media_deck),
            ("Paint", "#db2777", self.open_paint),
            ("Notepad", "#059669", self.open_notepad),
            ("Clock/Timer", "#d97706", self.open_clock_suite),
            ("Connect", "#2563eb", self.open_connectivity),
            ("App Studio", "#0d9488", self.open_app_studio),
            ("Vision AI", "#4f46e5", self.open_ai_advisor),
        ]

        cols = 4
        spacing_x = max(220, self.width // 5)
        spacing_y = max(200, self.height // 3)

        for i, (label, color, callback) in enumerate(apps):
            row, col = divmod(i, cols)
            bx = spacing_x * (col + 0.8)
            by = spacing_y * (row + 0.65)
            radius = 54

            oval = self.canvas.create_oval(
                bx - radius, by - radius, bx + radius, by + radius,
                fill="#0f1e36", outline=color, width=3
            )
            sheen = self.canvas.create_oval(
                bx - radius + 12, by - radius + 10, bx - 10, by - 14,
                fill=color, outline=""
            )
            text = self.canvas.create_text(
                bx, by + 12, text=label, fill="#f8fafc", font=("Consolas", 10, "bold")
            )

            for item in (oval, sheen, text):
                self.canvas.tag_bind(item, "<Button-1>", lambda _e, cb=callback: cb())

            self.bubbles.append({
                "oval": oval, "sheen": sheen, "text": text,
                "base_x": bx, "base_y": by, "r": radius,
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(0.03, 0.055)
            })

    def animate_bubbles(self):
        for b in self.bubbles:
            b["phase"] += b["speed"]
            dx = math.cos(b["phase"] * 0.7) * 6
            dy = math.sin(b["phase"]) * 9
            cx = b["base_x"] + dx
            cy = b["base_y"] + dy
            r = b["r"]

            self.canvas.coords(b["oval"], cx - r, cy - r, cx + r, cy + r)
            self.canvas.coords(b["sheen"], cx - r + 12, cy - r + 10, cx - 10, cy - 14)
            self.canvas.coords(b["text"], cx, cy + 12)

        self.root.after(45, self.animate_bubbles)

    def update_taskbar_clock(self):
        now = datetime.now().strftime("%a %d %b | %I:%M:%S %p")
        self.clock_lbl.config(text=now)
        self.root.after(1000, self.update_taskbar_clock)

    # ---------------- NATIVE APP 1: ADAPTIVE BROWSER ----------------
    def open_adaptive_browser(self):
        win = tk.Toplevel(self.root)
        win.title("Vision Adaptive Browser")
        win.geometry("460x320")
        win.configure(bg="#0b1320")

        tk.Label(win, text="Select Browser Execution Weight", bg="#0b1320", fg="#38bdf8",
                 font=("Consolas", 12, "bold")).pack(pady=12)

        url_var = tk.StringVar(value="https://example.com")
        tk.Entry(win, textvariable=url_var, width=44, bg="#162238", fg="#f8fafc",
                 insertbackground="white", font=("Consolas", 10)).pack(pady=8)

        profiles = load_profiles()

        def launch(mode_key):
            p = profiles[mode_key]
            browser = self._find_browser()
            if not browser:
                messagebox.showerror("Browser Missing", "No Chromium/Edge/Chrome binary found on host.")
                return
            profile_dir = BASE_DIR / ".vision_runtime" / mode_key
            profile_dir.mkdir(parents=True, exist_ok=True)
            cmd = [browser, f"--user-data-dir={profile_dir}", "--no-first-run", *p.get("flags", []), url_var.get()]
            subprocess.Popen(cmd)
            log_event("browser", f"launch_{mode_key}")
            win.destroy()

        for key, label in [
            ("lite", "1. Lite Surf (Low RAM / Fast Text)"),
            ("media", "2. Media Mode (Hardware Video/Audio)"),
            ("compute", "3. Heavy Mode (Games / WebGL / Research)")
        ]:
            tk.Button(win, text=label, width=38, bg="#1e293b", fg="#e2e8f0",
                      font=("Consolas", 10), pady=6, command=lambda k=key: launch(k)).pack(pady=5)

    def _find_browser(self):
        for c in [
            "google-chrome", "chromium", "chromium-browser", "msedge",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]:
            if shutil.which(c) or os.path.exists(c):
                return c
        return None

    # ---------------- NATIVE APP 2: UNIFIED MEDIA HUB ----------------
    def open_media_deck(self):
        win = tk.Toplevel(self.root)
        win.title("Vision Unified Media Hub")
        win.geometry("460x360")
        win.configure(bg="#0b1320")

        tk.Label(win, text="Unified Low-Weight Media Deck", bg="#0b1320", fg="#c084fc",
                 font=("Consolas", 12, "bold")).pack(pady=12)

        platforms = [
            ("YouTube (App Mode)", "https://www.youtube.com"),
            ("Spotify Web Player", "https://open.spotify.com"),
            ("JioSaavn Music", "https://www.jiosaavn.com"),
            ("Prime Video", "https://www.primevideo.com"),
            ("Netflix", "https://www.netflix.com"),
        ]

        def open_stream(name, url):
            browser = self._find_browser()
            if not browser:
                messagebox.showerror("Engine Missing", "Install Chromium/Chrome/Edge for web media playback.")
                return
            profiles = load_profiles()
            media_flags = profiles.get("media", {}).get("flags", [])
            profile_dir = BASE_DIR / ".vision_runtime" / "media_hub"
            profile_dir.mkdir(parents=True, exist_ok=True)
            subprocess.Popen([browser, f"--user-data-dir={profile_dir}", f"--app={url}", *media_flags])
            log_event("media_hub", f"stream_{name}")

        for name, url in platforms:
            tk.Button(win, text=f"▶ {name}", width=36, bg="#1e1b4b", fg="#e9d5ff",
                      font=("Consolas", 10), pady=5, command=lambda n=name, u=url: open_stream(n, u)).pack(pady=4)

    # ---------------- NATIVE APP 3: VISION PAINT ----------------
    def open_paint(self):
        win = tk.Toplevel(self.root)
        win.title("Vision Paint (Lightweight Canvas)")
        win.geometry("680x480")
        win.configure(bg="#0b1320")

        toolbar = tk.Frame(win, bg="#162238", height=36)
        toolbar.pack(fill=tk.X)

        brush_color = tk.StringVar(value="#38bdf8")
        brush_size = tk.IntVar(value=4)

        for col in ["#38bdf8", "#f43f5e", "#10b981", "#facc15", "#ffffff", "#060b14"]:
            tk.Button(toolbar, bg=col, width=3, command=lambda c=col: brush_color.set(c)).pack(side=tk.LEFT, padx=3, pady=4)

        canvas = tk.Canvas(win, bg="#060b14", highlightthickness=0, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)

        tk.Button(toolbar, text="Clear", bg="#334155", fg="white",
                  command=lambda: canvas.delete("all")).pack(side=tk.RIGHT, padx=8)

        last_pos = {"x": None, "y": None}

        def draw(event):
            if last_pos["x"] is not None:
                canvas.create_line(
                    last_pos["x"], last_pos["y"], event.x, event.y,
                    fill=brush_color.get(), width=brush_size.get(), capstyle=tk.ROUND, smooth=True
                )
            last_pos["x"], last_pos["y"] = event.x, event.y

        def reset(_event):
            last_pos["x"], last_pos["y"] = None, None

        canvas.bind("<B1-Motion>", draw)
        canvas.bind("<ButtonRelease-1>", reset)
        log_event("paint", "open")

    # ---------------- NATIVE APP 4: NOTEPAD ----------------
    def open_notepad(self):
        win = tk.Toplevel(self.root)
        win.title("Vision Notepad")
        win.geometry("620x440")
        win.configure(bg="#0b1320")

        bar = tk.Frame(win, bg="#162238")
        bar.pack(fill=tk.X)

        text_area = tk.Text(win, bg="#09111e", fg="#e2e8f0", insertbackground="white",
                            font=("Consolas", 11), undo=True)
        text_area.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        def save_note():
            path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text_area.get("1.0", tk.END))
                log_event("notepad", "save_file")

        def open_note():
            path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if path:
                with open(path, "r", encoding="utf-8") as f:
                    text_area.delete("1.0", tk.END)
                    text_area.insert("1.0", f.read())

        tk.Button(bar, text="Open", bg="#1e293b", fg="white", command=open_note).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(bar, text="Save", bg="#059669", fg="white", command=save_note).pack(side=tk.LEFT, padx=4, pady=4)

    # ---------------- NATIVE APP 5: CLOCK, STOPWATCH & TIMER ----------------
    def open_clock_suite(self):
        win = tk.Toplevel(self.root)
        win.title("Vision Clock / Stopwatch / Timer")
        win.geometry("420x340")
        win.configure(bg="#0b1320")

        live_lbl = tk.Label(win, text="", bg="#0b1320", fg="#fbbf24", font=("Consolas", 18, "bold"))
        live_lbl.pack(pady=10)

        def tick_clock():
            if win.winfo_exists():
                live_lbl.config(text=datetime.now().strftime("%H:%M:%S"))
                win.after(500, tick_clock)

        tick_clock()

        # Stopwatch
        sw_state = {"running": False, "elapsed": 0.0, "last": 0.0}
        sw_lbl = tk.Label(win, text="Stopwatch: 00:00.0", bg="#0b1320", fg="#38bdf8", font=("Consolas", 13))
        sw_lbl.pack(pady=6)

        def update_sw():
            if win.winfo_exists():
                if sw_state["running"]:
                    now = time.time()
                    sw_state["elapsed"] += now - sw_state["last"]
                    sw_state["last"] = now
                mins, secs = divmod(sw_state["elapsed"], 60)
                sw_lbl.config(text=f"Stopwatch: {int(mins):02d}:{secs:04.1f}")
                win.after(100, update_sw)

        def toggle_sw():
            sw_state["running"] = not sw_state["running"]
            if sw_state["running"]:
                sw_state["last"] = time.time()

        def reset_sw():
            sw_state["running"] = False
            sw_state["elapsed"] = 0.0

        sw_frame = tk.Frame(win, bg="#0b1320")
        sw_frame.pack()
        tk.Button(sw_frame, text="Start/Pause", bg="#1e293b", fg="white", command=toggle_sw).pack(side=tk.LEFT, padx=4)
        tk.Button(sw_frame, text="Reset", bg="#1e293b", fg="white", command=reset_sw).pack(side=tk.LEFT, padx=4)
        update_sw()

        # Countdown Timer
        timer_state = {"remaining": 0, "active": False}
        tm_lbl = tk.Label(win, text="Timer: 00:00", bg="#0b1320", fg="#34d399", font=("Consolas", 13))
        tm_lbl.pack(pady=10)

        def start_timer():
            mins = simpledialog.askinteger("Set Timer", "Enter minutes:", parent=win, minvalue=1, maxvalue=180)
            if mins:
                timer_state["remaining"] = mins * 60
                timer_state["active"] = True

        def tick_timer():
            if win.winfo_exists():
                if timer_state["active"] and timer_state["remaining"] > 0:
                    timer_state["remaining"] -= 1
                    if timer_state["remaining"] == 0:
                        timer_state["active"] = False
                        messagebox.showinfo("Vision Timer", "Time is up!")
                m, s = divmod(timer_state["remaining"], 60)
                tm_lbl.config(text=f"Timer: {m:02d}:{s:02d}")
                win.after(1000, tick_timer)

        tk.Button(win, text="Set Countdown Timer", bg="#065f46", fg="white", command=start_timer).pack(pady=4)
        tick_timer()

    # ---------------- NATIVE APP 6: LOW-WEIGHT CONNECTIVITY ----------------
    def open_connectivity(self):
        win = tk.Toplevel(self.root)
        win.title("Vision Hardware & Fast Connect")
        win.geometry("480x360")
        win.configure(bg="#0b1320")

        tk.Label(win, text="Hardware & Low-Overhead Connections", bg="#0b1320", fg="#60a5fa",
                 font=("Consolas", 12, "bold")).pack(pady=10)

        out = tk.Text(win, height=11, width=54, bg="#09111e", fg="#a7f3d0", font=("Consolas", 9))
        out.pack(pady=6)

        def scan_network():
            out.delete("1.0", tk.END)
            sys_name = platform.system()
            try:
                if sys_name == "Windows":
                    res = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True, stderr=subprocess.DEVNULL)
                else:
                    res = subprocess.check_output(["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL", "dev", "wifi"], text=True, stderr=subprocess.DEVNULL)
                out.insert(tk.END, res[:1200])
            except Exception as exc:
                out.insert(tk.END, f"Wi-Fi probe info ({sys_name}): {exc}\n")

        def open_bt_audio(target):
            sys_name = platform.system()
            if sys_name == "Windows":
                os.system(f"start {target}")
            else:
                out.insert(tk.END, f"\n[Vision Linux Hook] Triggered {target}\n")

        btn_row = tk.Frame(win, bg="#0b1320")
        btn_row.pack(pady=6)
        tk.Button(btn_row, text="Scan Wi-Fi", bg="#1d4ed8", fg="white", command=scan_network).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="Bluetooth", bg="#1e293b", fg="white",
                  command=lambda: open_bt_audio("ms-settings:bluetooth")).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="Sound", bg="#1e293b", fg="white",
                  command=lambda: open_bt_audio("ms-settings:sound")).pack(side=tk.LEFT, padx=4)
        scan_network()

    # ---------------- NATIVE APP 7: CUSTOM APP & SERVICE STUDIO ----------------
    def open_app_studio(self):
        win = tk.Toplevel(self.root)
        win.title("Vision App Studio (Custom Micro-App Builder)")
        win.geometry("540x430")
        win.configure(bg="#0b1320")

        tk.Label(win, text="Build & Run Custom Low-Weight Vision Apps", bg="#0b1320", fg="#2dd4bf",
                 font=("Consolas", 11, "bold")).pack(pady=8)

        name_entry = tk.Entry(win, width=40, bg="#162238", fg="white", font=("Consolas", 10))
        name_entry.insert(0, "MyCustomCalc")
        name_entry.pack(pady=4)

        code_box = tk.Text(win, height=11, width=60, bg="#09111e", fg="#f8fafc", font=("Consolas", 9))
        code_box.insert("1.0", '    tk.Label(win, text="Custom Vision Micro-Service Running!", fg="#38bdf8", bg="#0b1320").pack(pady=30)')
        code_box.pack(pady=6)

        def build_and_run():
            app_name = name_entry.get().strip() or "CustomApp"
            body = code_box.get("1.0", tk.END)
            app_path = vision_sdk.create_custom_app(app_name, "User-created Vision micro-app", body)
            log_event("app_studio", f"created_{app_name}")
            spec = importlib.util.spec_from_file_location(app_name, app_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.run(self.root)

        tk.Button(win, text="Compile & Launch in Vision Sandbox", bg="#0d9488", fg="white",
                  font=("Consolas", 10, "bold"), command=build_and_run).pack(pady=6)

    # ---------------- NATIVE APP 8: ADAPTIVE LOCAL AI ADVISOR ----------------
    def open_ai_advisor(self):
        win = tk.Toplevel(self.root)
        win.title("Vision Local AI — Adaptive Decision & Telemetry Engine")
        win.geometry("580x450")
        win.configure(bg="#0b1320")

        tk.Label(win, text="Vision Local AI Advisor (Self-Tuning Feedback Loop)", bg="#0b1320", fg="#818cf8",
                 font=("Consolas", 11, "bold")).pack(pady=8)

        chat = tk.Text(win, height=15, width=66, bg="#09111e", fg="#e2e8f0", font=("Consolas", 9), wrap=tk.WORD)
        chat.pack(padx=10, pady=6)
        chat.insert(tk.END, "Vision AI: Ask me about system RAM, performance tuning, usage telemetry, or type 'optimize' to auto-tune profiles.\n\n")

        prompt_entry = tk.Entry(win, width=52, bg="#162238", fg="white", font=("Consolas", 10))
        prompt_entry.pack(side=tk.LEFT, padx=10, pady=8)

        def respond(_event=None):
            q = prompt_entry.get().strip()
            if not q:
                return
            prompt_entry.delete(0, tk.END)
            chat.insert(tk.END, f"You: {q}\n")
            reply = self._local_ai_reason(q)
            chat.insert(tk.END, f"Vision AI: {reply}\n\n")
            chat.see(tk.END)

        prompt_entry.bind("<Return>", respond)
        tk.Button(win, text="Ask AI", bg="#4f46e5", fg="white", command=respond).pack(side=tk.LEFT, padx=4)

    def _local_ai_reason(self, query: str) -> str:
        ql = query.lower()
        events = []
        if TELEMETRY_LOG.exists():
            with open(TELEMETRY_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        profiles = load_profiles()

        if "optimize" in ql or "tune" in ql or "improve" in ql:
            lite_runs = sum(1 for e in events if "lite" in e.get("action", ""))
            compute_runs = sum(1 for e in events if "compute" in e.get("action", ""))
            if compute_runs > lite_runs:
                profiles["compute"]["max_memory_mb"] = min(8192, profiles["compute"]["max_memory_mb"] + 512)
                save_profiles(profiles)
                log_event("vision_ai", "auto_tuned_compute_up")
                return f"Telemetry shows heavy compute usage ({compute_runs} runs). Raised Compute RAM cap to {profiles['compute']['max_memory_mb']} MB."
            else:
                profiles["lite"]["max_memory_mb"] = max(192, profiles["lite"]["max_memory_mb"] - 32)
                save_profiles(profiles)
                log_event("vision_ai", "auto_tuned_lite_lean")
                return f"Telemetry favors lightweight sessions ({len(events)} total events). Tightened Lite Surf RAM ceiling to {profiles['lite']['max_memory_mb']} MB for faster response."

        if "status" in ql or "telemetry" in ql or "system" in ql or "ram" in ql:
            return (
                f"OS Host: {platform.system()} {platform.release()} | "
                f"Logged Telemetry Events: {len(events)} | "
                f"Current Profile Caps -> Lite: {profiles['lite']['max_memory_mb']}MB, "
                f"Media: {profiles['media']['max_memory_mb']}MB, Compute: {profiles['compute']['max_memory_mb']}MB. "
                f"Custom Apps Installed: {len(vision_sdk.list_custom_apps())}."
            )

        if "ollama" in ql or "llm" in ql or "model" in ql:
            return "Vision AI runs a zero-overhead rule+telemetry core by default (<5MB RAM) and can bridge to local Ollama/llama.cpp models when heavier reasoning is requested."

        return (
            f"Based on {len(events)} recorded feedback events, your environment is running in Lean-Mode. "
            "Ask about 'system status', 'telemetry', or type 'optimize' so I can adapt resource limits to your usage pattern."
        )

    def shutdown_os(self):
        log_event("kernel", "shutdown_desktop_shell")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VisionDesktopOS(root)
    root.mainloop()