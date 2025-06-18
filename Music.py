import os
import re
import requests
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC, USLT, error
from mutagen.mp4 import MP4, MP4Cover

TEMP_DIR = "temp_metadata"
os.makedirs(TEMP_DIR, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def clear_old_covers():
    for f in os.listdir(TEMP_DIR):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            try:
                os.remove(os.path.join(TEMP_DIR, f))
            except Exception:
                pass

def search_deezer(artist, title):
    query = f"{artist} {title}"
    url = f"https://api.deezer.com/search?q={requests.utils.quote(query)}"
    res = requests.get(url).json()
    if res.get("data"):
        return res["data"][0]
    return None

def get_lyrics(artist, title):
    try:
        url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
        res = requests.get(url).json()
        return res.get("lyrics")
    except:
        return None

def download_cover(url, artist, song_title):
    clear_old_covers()
    r = requests.get(url)
    if r.status_code == 200:
        content_type = r.headers.get("Content-Type", "")
        ext = "jpg"
        mime = "image/jpeg"
        if "png" in content_type:
            ext = "png"
            mime = "image/png"
        elif "webp" in content_type:
            ext = "webp"
            mime = "image/webp"

        safe_artist = sanitize_filename(artist)
        safe_title = sanitize_filename(song_title)
        temp_filename = f"temp_cover.{ext}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)

        with open(temp_path, 'wb') as f:
            f.write(r.content)

        new_cover_path = rename_cover_image(temp_path, artist, song_title)
        return new_cover_path, mime
    return None, None

def rename_cover_image(old_path, artist, song_title):
    folder = os.path.dirname(old_path)
    safe_artist = sanitize_filename(artist)
    safe_title = sanitize_filename(song_title)
    new_name = f"{safe_artist} - {safe_title}.jpg"
    new_path = os.path.join(folder, new_name)

    if os.path.abspath(old_path) != os.path.abspath(new_path):
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(old_path, new_path)
    return new_path

def embed_metadata(file_path, artist, title, album, year, lyrics, cover_path, cover_mime, genre):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".mp3":
        audio = MP3(file_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass

        audio.tags.delall("APIC")
        audio.tags["TPE1"] = TPE1(encoding=3, text=artist)
        audio.tags["TIT2"] = TIT2(encoding=3, text=title)
        audio.tags["TALB"] = TALB(encoding=3, text=album)
        if year:
            audio.tags["TDRC"] = TDRC(encoding=3, text=str(year))
        audio.tags["TCON"] = TCON(encoding=3, text="")  # Always blank
        if lyrics:
            audio.tags.delall("USLT")
            audio.tags.add(USLT(encoding=3, lang="eng", desc="desc", text=lyrics))
        if cover_path and cover_mime != "image/webp":
            with open(cover_path, 'rb') as img:
                audio.tags.add(APIC(
                    encoding=3,
                    mime=cover_mime,
                    type=3,
                    desc="Cover",
                    data=img.read()
                ))
        audio.save()

    elif ext == ".m4a":
        audio = MP4(file_path)
        audio["\xa9ART"] = [artist]
        audio["\xa9nam"] = [title]
        audio["\xa9alb"] = [album]
        if year:
            audio["\xa9day"] = [str(year)]
        audio["\xa9gen"] = [""]  # Always blank
        if lyrics:
            audio["\xa9lyr"] = [lyrics]
        if cover_path:
            with open(cover_path, 'rb') as img:
                fmt = MP4Cover.FORMAT_PNG if "png" in cover_mime else MP4Cover.FORMAT_JPEG
                audio["covr"] = [MP4Cover(img.read(), imageformat=fmt)]
        audio.save()
    else:
        raise Exception("Unsupported format. Only .mp3 and .m4a are supported.")

def rename_file_based_on_metadata(file_path, artist, title):
    directory = os.path.dirname(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    safe_artist = sanitize_filename(artist).strip()
    safe_title = sanitize_filename(title).strip()
    new_filename = f"{safe_artist} - {safe_title}{ext}"
    new_filename = re.sub(r'\s+', ' ', new_filename)  # remove multiple spaces
    new_path = os.path.join(directory, new_filename)

    if os.path.abspath(new_path) != os.path.abspath(file_path):
        try:
            os.rename(file_path, new_path)
            return new_path
        except Exception as e:
            print(f"Rename failed: {e}")
    return file_path

def ask_text(prompt, default=""):
    top = Toplevel()
    top.title(prompt)
    top.geometry("400x120+" + str((top.winfo_screenwidth() - 400) // 2) + "+" + str((top.winfo_screenheight() - 120) // 2))
    Label(top, text=prompt).pack(pady=5)
    entry = Entry(top, width=50)
    entry.pack(padx=10, pady=5)
    entry.insert(0, default)
    entry.focus()

    result = []

    def on_submit():
        result.append(entry.get())
        top.destroy()

    Button(top, text="OK", command=on_submit).pack(pady=5)
    top.wait_window()
    return result[0] if result else None

def guess_artist_title(filename):
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r'(\(|\[)?lyrics(\)|\])?', '', name, flags=re.IGNORECASE).strip()
    for sep in [' - ', '_', '.', '–']:
        if sep in name:
            parts = name.split(sep)
            if len(parts) >= 2:
                artist = parts[0].strip()
                title = sep.join(parts[1:]).strip()
                return artist, title
    return "", name

class MetadataEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Metadata Editor")
        self.center_window(400, 150)

        self.status_label = Label(root, text="Select songs to start.", pady=5)
        self.status_label.pack()

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.another_btn = Button(root, text="Select More Songs", state=DISABLED, command=self.select_files)
        self.another_btn.pack(pady=10)

        self.side_window = None
        self.files_to_process = []
        self.current_index = 0
        self.file_status_labels = []

        root.after(100, self.select_files)

    def center_window(self, w, h):
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def select_files(self):
        files = filedialog.askopenfilenames(title="Select Audio Files", filetypes=[("Audio files", "*.mp3 *.m4a")])
        if files:
            self.files_to_process = list(files)
            self.current_index = 0
            self.status_label.config(text=f"{len(files)} files selected.")
            self.progress["maximum"] = len(files)
            self.progress["value"] = 0
            self.create_side_window()
            self.process_next_song()

    def create_side_window(self):
        if self.side_window:
            self.side_window.destroy()
        self.side_window = Toplevel(self.root)
        self.side_window.title("Processing Queue")
        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y()
        self.side_window.geometry(f"300x400+{x}+{y}")
        self.file_status_labels = []
        for file in self.files_to_process:
            lbl = Label(self.side_window, text=f"🕐 {os.path.basename(file)}", anchor="w")
            lbl.pack(fill="x", padx=5, pady=2)
            self.file_status_labels.append(lbl)

    def update_file_status(self, index, status):
        if index < len(self.file_status_labels):
            self.file_status_labels[index].config(text=f"{status} {os.path.basename(self.files_to_process[index])}")

    def process_next_song(self):
        if self.current_index >= len(self.files_to_process):
            self.status_label.config(text="All files processed.")
            self.another_btn.config(state=NORMAL)
            return

        file_path = self.files_to_process[self.current_index]
        self.update_file_status(self.current_index, "⚙️ Processing")

        guessed_artist, guessed_title = guess_artist_title(file_path)
        artist = ask_text("Enter Artist Name", default=guessed_artist)
        if not artist:
            self.status_label.config(text="Artist name input cancelled.")
            return

        title = ask_text("Enter Song Title", default=guessed_title)
        if not title:
            self.status_label.config(text="Song title input cancelled.")
            return

        meta = search_deezer(artist, title)
        if not meta:
            messagebox.showerror("Not Found", "No metadata found.")
            self.status_label.config(text="Metadata not found.")
            return

        main_artist = meta["artist"]["name"]
        title = meta["title"]
        album = meta["album"]["title"]
        year = meta.get("release_date", "").split("-")[0] if meta.get("release_date") else ""
        genre = ""
        cover_url = meta["album"].get("cover_xl") or meta["album"].get("cover_big")
        cover_path, cover_mime = download_cover(cover_url, main_artist, title)
        lyrics = get_lyrics(main_artist, title)
        if lyrics:
            lyrics = re.sub(r'\[.*?\]', '', lyrics).strip()
        else:
            messagebox.showinfo("Lyrics", "No lyrics found.")

        try:
            embed_metadata(file_path, main_artist, title, album, year, lyrics, cover_path, cover_mime, genre)
            new_path = rename_file_based_on_metadata(file_path, main_artist, title)
            self.status_label.config(text=f"Processed: {os.path.basename(new_path)}")
            self.update_file_status(self.current_index, "✅ Done")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Error during metadata embedding.")
            self.update_file_status(self.current_index, "❌ Error")

        self.current_index += 1
        self.progress["value"] = self.current_index
        self.root.after(500, self.process_next_song)

def main():
    root = Tk()
    app = MetadataEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()