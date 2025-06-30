# 🎶 YouTube MP3 Downloader + Auto Metadata & Lyrics Embedder

A sleek, offline-capable **music tool** for Windows that lets you:

> ✅ Download any song from YouTube  
> 🧠 Automatically tag it with proper **artist, title, album, cover**, and **lyrics**  
> 🎧 Get clean `.mp3` or `.m4a` files, ready for your player or editor

No junk. No command line. Just double-click, search, download, and you're done. 🪄

---

## 🧩 What's Inside?

### 🎵 Download Songs.exe
> The YouTube song fetcher

- 🔍 Search up to 10 results from YouTube (adds the "lyrics" suffix at the end of the search to get cleaner files) or use directly the URL
- 🎯 Picks the best quality audio (~263kbit/s)
- 🧹 Automatically cleans titles (removes "lyrics", "official video", etc.)
- 📁 Saves the file as a proper `.mp3`
- 🎼 One-click button to open the metadata editor (`Music.exe`)

### 🎙️ Music.exe
> The metadata editor & lyrics injector

- 🧠 Detects artist & title automatically from filename
- 🌐 Fetches:
  - 🎨 Album, release year, HD cover art (from Deezer)
  - 📝 Full lyrics (from Lyrics.ovh)
- 🖊️ Embeds all metadata directly into the `.mp3` or `.m4a` file
- 🎼 Optionally renames file to `Artist - Title.mp3`
- ✅ Shows progress and lets you batch-process your library

---

## 🖥️ How to Use (Windows)

> ✅ No Python. No Terminal. No Hassle.

### 🔄 Step-by-step

1. 📦 **[Download the latest release](https://github.com/Brxownie/Music-for-iPod/releases)**
2. 🗂️ Extract the `.zip` anywhere
3. 🚀 Double-click `Download Songs.exe`
4. 🔎 Search your song and hit **Download**
5. 🎼 Click **"Open Music.exe"** to embed clean metadata + lyrics

🎉 You're done. Use now iTunes to upload them to the iPod. They'll look perfect.

### 🔄 Update

1. ❌ Erase the old one. Make sure that the songs are saved somewhere else
2. 🗂️ Extract the `.zip` and use it as said above.
---

## 🛠️ For Developers (Optional)

If you want to run or extend the Python source:
FFMPEG MUST BE IN PATH !

### 📦 Requirements
- Python 3.9+
- `yt-dlp`
- `mutagen`
- `requests`
- `tkinter` (usually built-in)

### ▶ Install dependencies

```bash
pip install -r requirements.txt
```
---

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — For YouTube downloading.
- [FFmpeg](https://ffmpeg.org/) — For audio and video processing.
- [mutagen](https://github.com/quodlibet/mutagen) — For audio metadata editing.
- [Deezer API](https://developers.deezer.com/api) — For artist, album, and cover data.
- [Lyrics.ovh](https://lyricsovh.docs.apiary.io) — For fetching plain lyrics.
- GUI and logic — handcrafted by [Brxownie](https://github.com/Brxownie) and ChatGPT.

