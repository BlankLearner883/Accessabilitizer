"""
Accessibility tools launcher — UI version (CustomTkinter).
Scans the current directory for files and lets you run each tool on applicable files.

Run: python accessible_ui.py

Requires: pip install customtkinter
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk


# File extensions each tool can use
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".wmv", ".flv"}
HTML_EXTENSIONS = {".html", ".htm"}


def script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))

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
            pass  # end of frames

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


def scan_directory(path: str) -> tuple[list[str], list[str]]:
    """Return (video_paths, html_paths) in the given directory."""
    videos: list[str] = []
    htmls: list[str] = []
    try:
        for name in os.listdir(path):
            full = os.path.join(path, name)
            if not os.path.isfile(full):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                videos.append(full)
            elif ext in HTML_EXTENSIONS:
                htmls.append(full)
    except OSError:
        pass
    return (sorted(videos), sorted(htmls))


def run_script(script_name: str, args: list[str], cwd: str) -> subprocess.Popen:
    """Start a Python script; returns the Popen object for the UI to track."""
    script_path = os.path.join(script_dir(), script_name)
    cmd = [sys.executable, script_path] + args
    return subprocess.Popen(
        cmd,
        cwd=cwd or script_dir(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


class AccessibleUI:
    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Accessibility tools")
        self.root.geometry("760x580")
        self.root.minsize(520, 420)

        self.work_dir = tk.StringVar(value=os.getcwd())
        self.videos: list[str] = []
        self.htmls: list[str] = []

        self._build_ui()
        self.refresh_files()

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 8}

        dir_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        dir_frame.pack(fill="x", **pad)
        ctk.CTkLabel(dir_frame, text="Directory:").pack(side="left", padx=(0, 8))
        self.dir_entry = ctk.CTkEntry(dir_frame, textvariable=self.work_dir, width=420)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(dir_frame, text="Browse…", width=100, command=self._browse_dir).pack(side="left", padx=4)
        ctk.CTkButton(dir_frame, text="Refresh", width=90, command=self.refresh_files).pack(side="left", padx=4)

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # ---- Subtitle tab ----
        sub_tab = self.tabview.add("Subtitle (burn-in)")
        ctk.CTkLabel(
            sub_tab,
            text="Video → burn-in subtitles (faster-whisper + ffmpeg)",
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(sub_tab, text="Video file:", anchor="w").pack(anchor="w", pady=(12, 4))
        self.sub_combo = ctk.CTkComboBox(sub_tab, values=[], width=680, state="readonly")
        self.sub_combo.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(sub_tab, text="Run subtitle", command=self._run_subtitle).pack(anchor="w")
        self.sub_loader = GifPlayer(sub_tab, os.path.join("gui", "subtitle.gif"))

        # ---- Flicker tab ----
        fl_tab = self.tabview.add("Flicker reduction")
        ctk.CTkLabel(
            fl_tab,
            text="Video → reduce flicker (writes <name>_flicker.mp4)",
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(fl_tab, text="Video file:", anchor="w").pack(anchor="w", pady=(12, 4))
        self.fl_combo = ctk.CTkComboBox(fl_tab, values=[], width=680, state="readonly")
        self.fl_combo.pack(fill="x", pady=(0, 8))
        th_row = ctk.CTkFrame(fl_tab, fg_color="transparent")
        th_row.pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(th_row, text="Luminance threshold (e.g. 0.4):").pack(side="left", padx=(0, 8))
        self.fl_threshold = ctk.CTkEntry(th_row, width=80)
        self.fl_threshold.insert(0, "0.4")
        self.fl_threshold.pack(side="left")
        ctk.CTkButton(fl_tab, text="Run flicker reduction", command=self._run_flicker).pack(anchor="w")
        self.fl_loader = GifPlayer(fl_tab, os.path.join("gui", "flicker.gif"))

        # ---- Dyslexia tab ----
        dys_tab = self.tabview.add("Dyslexia (OpenDyslexic)")
        ctk.CTkLabel(
            dys_tab,
            text="HTML → apply OpenDyslexic font (writes <name>_dyslexia.html)",
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(dys_tab, text="HTML file:", anchor="w").pack(anchor="w", pady=(12, 4))
        self.dys_combo = ctk.CTkComboBox(dys_tab, values=[], width=680, state="readonly")
        self.dys_combo.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(dys_tab, text="Run dyslexia", command=self._run_dyslexia).pack(anchor="w")
        self.dys_loader = GifPlayer(dys_tab, os.path.join("gui", "dyslexia.gif"))

        # ---- Caption tab ----
        cap_tab = self.tabview.add("Image captions")
        ctk.CTkLabel(
            cap_tab,
            text="HTML with images → add BLIP captions (writes *_captioned.html)",
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(cap_tab, text="HTML file:", anchor="w").pack(anchor="w", pady=(12, 4))
        self.cap_combo = ctk.CTkComboBox(cap_tab, values=[], width=680, state="readonly")
        self.cap_combo.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(cap_tab, text="Run image caption", command=self._run_caption).pack(anchor="w")
        self.cap_loader = GifPlayer(cap_tab, os.path.join("gui", "caption.gif"))

        ctk.CTkLabel(self.root, text="Output:", anchor="w").pack(anchor="w", padx=12, pady=(0, 4))
        self.log = ctk.CTkTextbox(self.root, height=160, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log.configure(state="disabled")

    def _browse_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self.work_dir.get() or os.getcwd())
        if path:
            self.work_dir.set(path)
            self.refresh_files()

    def refresh_files(self) -> None:
        path = self.work_dir.get().strip() or os.getcwd()
        if not os.path.isdir(path):
            self.log_append(f"Not a directory: {path}\n")
            return
        self.videos, self.htmls = scan_directory(path)

        self.sub_combo.configure(values=self.videos)
        self.fl_combo.configure(values=self.videos)
        self.dys_combo.configure(values=self.htmls)
        self.cap_combo.configure(values=self.htmls)

        if self.videos:
            self.sub_combo.set(self.videos[0])
            self.fl_combo.set(self.videos[0])
        else:
            self.sub_combo.set("")
            self.fl_combo.set("")

        if self.htmls:
            self.dys_combo.set(self.htmls[0])
            self.cap_combo.set(self.htmls[0])
        else:
            self.dys_combo.set("")
            self.cap_combo.set("")

        self.log_append(f"Scanned {path}: {len(self.videos)} video(s), {len(self.htmls)} HTML file(s).\n")

    def log_append(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _run(self, script_name, args, description, loader=None):
        path = self.work_dir.get().strip() or os.getcwd()
        cwd = path if os.path.isdir(path) else script_dir()

        self.log_append(f"\n--- {description} ---\n")
        self.log_append(" ".join([script_name] + args) + "\n")

        if loader:
            self.root.after(0, loader.start)

        def run_in_thread():
            try:
                proc = run_script(script_name, args, cwd)

                if proc.stdout:
                    for line in proc.stdout:
                        self.root.after(0, lambda l=line: self.log_append(l))

                proc.wait()

                if loader:
                    self.root.after(0, loader.stop)

                if proc.returncode == 0:
                    self.root.after(0, lambda: self.log_append("Done.\n"))
                else:
                    self.root.after(0, lambda: self.log_append(f"Exit code: {proc.returncode}\n"))

            except Exception as e:
                if loader:
                    self.root.after(0, loader.stop)

                self.root.after(0, lambda: self.log_append(f"Error: {e}\n"))
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=run_in_thread, daemon=True).start()

    def _run_subtitle(self) -> None:
        val = self.sub_combo.get().strip()
        if not val or not os.path.isfile(val):
            messagebox.showwarning("No file", "Select a video file.")
            return
        self._run("audio_subtitle.py", [val, "--no-pause"], "Subtitle burn-in")

    def _run_flicker(self) -> None:
        val = self.fl_combo.get().strip()
        if not val or not os.path.isfile(val):
            messagebox.showwarning("No file", "Select a video file.")
            return
        th = self.fl_threshold.get().strip() or "0.4"
        self._run("flicker.py", [val, th], "Flicker reduction")

    def _run_dyslexia(self) -> None:
        val = self.dys_combo.get().strip()
        if not val or not os.path.isfile(val):
            messagebox.showwarning("No file", "Select an HTML file.")
            return
        self._run("dyslexia.py", [val], "Dyslexia (OpenDyslexic)")

    def _run_caption(self) -> None:
        val = self.cap_combo.get().strip()
        if not val or not os.path.isfile(val):
            messagebox.showwarning("No file", "Select an HTML file.")
            return
        try:
            with open(val, "r", encoding="utf-8") as f:
                html_text = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read HTML: {e}")
            return

        img_srcs: list[str] = []
        img_srcs += re.findall(r'<img[^>]+src="([^"]+)"', html_text, flags=re.IGNORECASE)
        img_srcs += re.findall(r"<img[^>]+src='([^']+)'", html_text, flags=re.IGNORECASE)
        seen: set[str] = set()
        unique_srcs: list[str] = []
        for s in img_srcs:
            if s not in seen:
                seen.add(s)
                unique_srcs.append(s)

        base, ext = os.path.splitext(val)
        output_path = base + "_captioned" + (ext or ".html")

        lines = [
            "Planned changes:",
            f"- Input: {val}",
            f"- Output: {output_path}",
            f"- Images found: {len(unique_srcs)}",
            '- For each image, insert a <p class="caption"> right after it.',
            "- Image src list:",
        ]
        if not unique_srcs:
            lines.append("  (none)")
        else:
            for s in unique_srcs:
                lines.append(f"  - {s}")

        summary = "\n".join(lines)
        if not messagebox.askyesno("Confirm image caption changes", summary):
            return

        self._run("image_caption.py", [val, "--yes"], "Image captions")


def main() -> None:
    ctk.set_appearance_mode("system")
    root = ctk.CTk()
    ctk.set_default_color_theme("gui/blue.json")
    AccessibleUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
