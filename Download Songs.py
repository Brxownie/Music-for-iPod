import os
import re
import subprocess
import threading
import sys
from tkinter import *
from tkinter import messagebox, ttk

def clean_title(title):
    title = re.sub(r'[\[\(]?[^\[\]\(\)]*lyrics[^\[\]\(\)]*[\]\)]?', '', title, flags=re.IGNORECASE)
    title = re.sub(r'official\s*(audio|video)?', '', title, flags=re.IGNORECASE)
    title = re.sub(r'lyric(s)?', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\\/*?:"<>|]', '', title).strip(" -_")
    return title.strip()

def get_unique_filename(name):
    base, ext = os.path.splitext(name)
    counter = 1
    while os.path.exists(f"{base}{ext}"):
        base = re.sub(r"\(\d+\)$", "", base).strip()
        name = f"{base} ({counter}){ext}"
        counter += 1
    return name

def get_app_dir():
    return os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))

def get_yt_dlp_path():
    return os.path.join(get_app_dir(), "yt-dlp.exe")

def get_ffmpeg_path():
    return os.path.join(get_app_dir(), "ffmpeg.exe")

def ensure_binaries_exist():
    missing = []
    if not os.path.exists(get_yt_dlp_path()):
        missing.append("yt-dlp.exe\nhttps://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe")
    if not os.path.exists(get_ffmpeg_path()):
        missing.append("ffmpeg.exe\nhttps://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
    if not missing:
        return True
    messagebox.showerror(
        "Missing Tools",
        "The following required tools are missing from the same folder as this app:\n\n"
        + "\n\n".join(missing)
        + "\n\nPlease download them manually and place them next to this program."
    )
    return False

def run_silent(*args, **kwargs):
    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    return subprocess.run(*args, **kwargs)

def popen_silent(*args, **kwargs):
    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    return subprocess.Popen(*args, **kwargs)

def yt_search(query):
    if not ensure_binaries_exist():
        return []
    result = run_silent(
        [get_yt_dlp_path(), f"ytsearch10:{query}", "--flat-playlist", "--print", "%(title)s|%(id)s|%(uploader)s"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    lines = result.stdout.strip().split('\n')
    parsed = []
    for line in lines:
        parts = line.split("|")
        if len(parts) == 3:
            parsed.append(tuple(parts))
    return parsed

def get_video_title(video_id):
    try:
        result = run_silent(
            [get_yt_dlp_path(), f"https://www.youtube.com/watch?v={video_id}", "--get-title"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        return result.stdout.strip()
    except Exception:
        return f"youtube_{video_id}"

def download_song(video_id, title, update_status):
    if not ensure_binaries_exist():
        update_status("❌ Missing yt-dlp or ffmpeg.")
        return

    clean_name = clean_title(title)
    safe_title = get_unique_filename(f"{clean_name}.mp3")
    update_status(f"⬇️ Downloading: {safe_title}...")

    cmd = [
        get_yt_dlp_path(), f"https://www.youtube.com/watch?v={video_id}",
        "-f", "bestaudio",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "--ffmpeg-location", get_ffmpeg_path(),
        "-o", safe_title,
        "--no-playlist", "--quiet"
    ]

    run_silent(cmd)
    update_status(f"✅ Downloaded: {safe_title}")

def open_music_exe():
    try:
        exe_path = os.path.join(get_app_dir(), "Music.exe")
        popen_silent([exe_path], shell=True)
    except Exception as e:
        print("Error opening Music.exe:", e)

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 YouTube Song Downloader")
        self.root.geometry("900x600")
        self.root.configure(bg="#f3f3f3")
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", font=("Segoe UI", 10), background="#f3f3f3")

        frame = Frame(self.root, bg="#f3f3f3")
        frame.pack(pady=15)

        ttk.Label(frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_var = StringVar()
        self.search_entry = ttk.Entry(frame, textvariable=self.search_var, width=60)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.search_button = ttk.Button(frame, text="Search", command=self.perform_search)
        self.search_button.grid(row=0, column=2, padx=5)

        self.include_lyrics_var = BooleanVar(value=True)
        self.lyrics_checkbox = ttk.Checkbutton(frame, text="Music", variable=self.include_lyrics_var)
        self.lyrics_checkbox.grid(row=0, column=3, padx=10)

        self.music_btn = ttk.Button(self.root, text="🎼 Open Music.exe", command=open_music_exe)
        self.music_btn.pack(side=RIGHT, padx=12, pady=6)

        self.canvas = Canvas(self.root, bg="#ffffff", highlightthickness=0)
        self.scrollbar = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.result_frame = Frame(self.canvas, bg="#ffffff")
        self.canvas.create_window((0, 0), window=self.result_frame, anchor="nw")
        self.result_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.status_label = ttk.Label(self.root, text="Ready", anchor="w")
        self.status_label.pack(fill=X, padx=10, pady=5)

    def clear_results(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def update_status(self, msg):
        self.status_label.config(text=msg)

    def perform_search(self):
        query = self.search_var.get().strip()
        if not query:
            return

        is_url = query.startswith("http://") or query.startswith("https://")
        if not is_url and self.include_lyrics_var.get():
            query += " lyrics"

        self.clear_results()

        if is_url:
            match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", query)
            if match:
                video_id = match.group(1)
                self.update_status("🔍 Getting video title...")
                def fetch_and_download():
                    title = get_video_title(video_id)
                    download_song(video_id, title, self.update_status)
                threading.Thread(target=fetch_and_download, daemon=True).start()
            else:
                self.update_status("❌ Invalid YouTube URL")
        else:
            self.update_status(f"🔎 Searching: {query}...")
            threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query):
        try:
            results = yt_search(query)
            self.display_results(results)
        except Exception as e:
            self.update_status(f"❌ Error: {e}")

    def display_results(self, results):
        self.clear_results()
        if not results:
            ttk.Label(self.result_frame, text="No results found.", background="#ffffff").pack(pady=10)
            return

        for title, vid, uploader in results:
            row = Frame(self.result_frame, bg="#ffffff")
            row.pack(fill=X, padx=5, pady=6)

            left = Frame(row, bg="#ffffff")
            left.pack(side=LEFT, fill=BOTH, expand=True)

            Label(left, text=title, anchor="w", bg="#ffffff", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            Label(left, text=f"by {uploader}", anchor="w", bg="#ffffff", font=("Segoe UI", 9, "italic"), fg="gray").pack(anchor="w")

            ttk.Button(row, text="Download", command=lambda v=vid, t=title: threading.Thread(
                target=download_song,
                args=(v, t, self.update_status),
                daemon=True
            ).start()).pack(side=RIGHT, padx=5)

if __name__ == "__main__":
    root = Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
