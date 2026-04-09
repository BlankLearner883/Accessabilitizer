"""
Accessibility tools launcher — UI version (CustomTkinter).
Scans the current directory for files and lets you run each tool on applicable files.

Run: python accessible_ui.py

Requires: pip install customtkinter
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".wmv", ".flv"}
HTML_EXTENSIONS = {".html", ".htm"}


def script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def theme_path() -> str:
    return os.path.join(script_dir(), "gui", "blue.json")


class GifPlayer:
    def __init__(self, parent, gif_path: str, delay: int = 50):
        self.parent = parent
        self.gif_path = gif_path
        self.delay = delay
        self.frames = []
        self.label = ctk.CTkLabel(parent, text="")
        self.running = False
        self.frame_index = 0
        self._load_frames()

    def _load_frames(self):
        try:
            i = 0
            while True:
                frame = tk.PhotoImage(file=self.gif_path, format=f"gif -index {i}")
                self.frames.append(frame)
                i += 1
        except Exception:
            pass

    def start(self):
        if not self.frames:
            return
        self.running = True
        self.label.pack(pady=6)
        self._animate()

    def stop(self):
        self.running = False
        self.label.pack_forget()

    def _animate(self):
        if not self.running:
            return
        frame = self.frames[self.frame_index]
        self.label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.parent.after(self.delay, self._animate)


def scan_directory(path: str):
    videos, htmls = [], []
    for name in os.listdir(path):
        full = os.path.join(path, name)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            videos.append(full)
        elif ext in HTML_EXTENSIONS:
            htmls.append(full)
    return sorted(videos), sorted(htmls)


def run_script(script_name, args, cwd):
    script_path = os.path.join(script_dir(), script_name)
    return subprocess.Popen(
        [sys.executable, script_path] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


class AccessibleUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Accessibility tools")
        self.root.geometry("760x620")

        self.work_dir = tk.StringVar(value=os.getcwd())
        self.original_html = None

        self._build_ui()
        self.refresh_files()

    def _browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.work_dir.get() or os.getcwd())
        if path:
            self.work_dir.set(path)
            self.refresh_files()

    def _build_ui(self):
        frame = ctk.CTkFrame(self.root)
        frame.pack(fill="x", padx=12, pady=8)

        self.dir_entry = ctk.CTkEntry(frame, textvariable=self.work_dir)
        self.dir_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(frame, text="Browse", command=self._browse_dir).pack(side="left", padx=5)
        ctk.CTkButton(frame, text="Refresh", command=self.refresh_files).pack(side="left")

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=8)

        # Tabs
        self.sub_combo = ctk.CTkComboBox(self.tabview.add("Subtitle"), values=[])
        self.sub_combo.pack(fill="x", pady=5)
        ctk.CTkButton(self.tabview.tab("Subtitle"), text="Run Subtitle", command=self._run_subtitle).pack()

        self.dys_combo = ctk.CTkComboBox(self.tabview.add("Dyslexia"), values=[])
        self.dys_combo.pack(fill="x", pady=5)
        ctk.CTkButton(self.tabview.tab("Dyslexia"), text="Run Dyslexia", command=self._run_dyslexia).pack()

        self.cap_combo = ctk.CTkComboBox(self.tabview.add("Caption"), values=[])
        self.cap_combo.pack(fill="x", pady=5)
        ctk.CTkButton(self.tabview.tab("Caption"), text="Run Caption", command=self._run_caption).pack()

        self.flicker_combo = ctk.CTkComboBox(self.tabview.add("Flicker"), values=[])
        self.flicker_combo.pack(fill="x", pady=5)
        ctk.CTkButton(self.tabview.tab("Flicker"), text="Run Flicker Reduction", command=self._run_flicker).pack()

        self.log = ctk.CTkTextbox(self.root, height=150)
        self.log.pack(fill="both", expand=True, padx=12, pady=8)

        ctk.CTkButton(self.root, text="Set as Original", command=self._set_original).pack(anchor="w", padx=12)
        ctk.CTkButton(self.root, text="Return to Original", command=self._return_to_original).pack(anchor="w", padx=12)
        ctk.CTkButton(self.root, text="All Combinations", command=self._all_combinations).pack(anchor="w", padx=12, pady=5)

    def refresh_files(self):
        path = self.work_dir.get()
        self.videos, self.htmls = scan_directory(path)

        for combo in [self.sub_combo, self.dys_combo, self.cap_combo, self.flicker_combo]:
            combo.configure(values=self.htmls)

        if self.htmls:
            self.original_html = self.htmls[0]
            for combo in [self.sub_combo, self.dys_combo, self.cap_combo, self.flicker_combo]:
                combo.set(self.htmls[0])

    def log_append(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def _set_original(self):
        val = self.sub_combo.get()
        if val:
            self.original_html = val
            self.log_append(f"Set original: {val}")

    def _return_to_original(self):
        if not self.original_html:
            return
        for combo in [self.sub_combo, self.dys_combo, self.cap_combo, self.flicker_combo]:
            combo.set(self.original_html)
        self.log_append(f"Returned to original: {self.original_html}")

    def _stream_process(self, proc: subprocess.Popen) -> None:
        """Read a process's stdout line-by-line and append to the log. Blocks until done."""
        for line in proc.stdout:
            self.root.after(0, lambda l=line.rstrip(): self.log_append(l))
        proc.wait()

    def _run_threaded(self, func):
        threading.Thread(target=func, daemon=True).start()

    def _run_subtitle(self):
        def _go():
            proc = run_script("audio_subtitle.py", [self.sub_combo.get(), "--no-pause"], self.work_dir.get())
            self._stream_process(proc)
        self._run_threaded(_go)

    def _run_dyslexia(self):
        def _go():
            proc = run_script("dyslexia.py", [self.dys_combo.get()], self.work_dir.get())
            self._stream_process(proc)
        self._run_threaded(_go)

    def _run_caption(self):
        def _go():
            proc = run_script("image_caption.py", [self.cap_combo.get(), "--yes"], self.work_dir.get())
            self._stream_process(proc)
        self._run_threaded(_go)

    def _run_flicker(self):
        def _go():
            proc = run_script("flicker.py", [self.flicker_combo.get()], self.work_dir.get())  # was "flicker_reduction.py" in _all_combinations; script is flicker.py
            self._stream_process(proc)
        self._run_threaded(_go)

    def _all_combinations(self):
        base = self.original_html
        if not base:
            return

        def run():
            cwd = self.work_dir.get()

            def run_block(script, args):
                proc = run_script(script, args, cwd)
                self._stream_process(proc)

            run_block("dyslexia.py", [base])
            dys = base.replace(".html", ".dyslexia.html")

            run_block("image_caption.py", [base, "--yes"])
            cap = base.replace(".html", "_captioned.html")

            run_block("audio_subtitle.py", [base, "--no-pause"])
            sub = base.replace(".html", "_subtitled.html")

            run_block("flicker.py", [base])  # fixed: was "flicker_reduction.py"
            flick = base.replace(".html", "_flicker.html")

            run_block("image_caption.py", [dys, "--yes"])
            run_block("audio_subtitle.py", [dys, "--no-pause"])
            run_block("audio_subtitle.py", [cap, "--no-pause"])

            dys_cap = dys.replace(".html", "_captioned.html")
            run_block("audio_subtitle.py", [dys_cap, "--no-pause"])
            run_block("audio_subtitle.py", [flick, "--no-pause"])

            self.root.after(0, lambda: self.log_append("All combinations done."))

        threading.Thread(target=run, daemon=True).start()


def main():
    ctk.set_appearance_mode("system")

    theme_file = theme_path()
    if os.path.exists(theme_file):
        ctk.set_default_color_theme(theme_file)
    else:
        print(f"Theme not found: {theme_file}")

    root = ctk.CTk()
    AccessibleUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
