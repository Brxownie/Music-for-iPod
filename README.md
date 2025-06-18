# 🎶 YouTube Song Downloader + Metadata Embedder

This project is a **modern, GUI-based toolkit** for downloading music from YouTube and automatically enriching your audio files with full metadata, including time-synced lyrics.

---

## ✨ Features

### 📥 YouTube Song Downloader
- Search YouTube for songs using a sleek Windows 11-style GUI
- Automatically removes junk like `(lyrics)`, `[official audio]`, etc. from titles
- Downloads **best audio quality**, converts to `.mp3`
- Displays video uploader/channel info
- One-click download button per result
- Opens the Metadata Embedder after download

### 🧠 Auto Metadata Embedder
- Drag & drop or batch-select MP3/M4A files
- Detect artist & title from filename automatically
- Fetches:
  - Artist
  - Title
  - Album
  - Year
  - Cover Art (in HD)
  - Lyrics
- Embeds synced lyrics from `.lrc` or online sources (SYLT frame)
- Renames files to `Artist - Title.mp3` (optional)
- Creates a side panel showing live status per file

---

## 📂 File Structure

```bash
/
├── downloader.py         # GUI YouTube music downloader
├── Music.py              # Auto metadata + synced lyrics embedder
├── temp_metadata/        # Temp folder for cover images
└── README.md             # You're reading it!
