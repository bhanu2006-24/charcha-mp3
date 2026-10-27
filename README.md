# 🎵 Charcha MP3 — YouTube to MP3 Studio

> **Audio-only YouTube video & full playlist downloader with universal MP3 playback, dedicated playlist folder organization, embedded album art, and instant mobile phone access.**

---

## ✨ Features

- 🎧 **Pure Audio Extraction**: Downloads high-quality audio with **zero video clutter**.
- 🌟 **Universal Compatibility**: Encoded with **ID3v2.3 tags** (Title, Artist, Album, Track Number, and Embedded Cover Art).
  - Works natively in **Apple Music**, **iOS Files**, **Spotify (Local Files)**, **Android music players (Musicolet, Retro, Poweramp)**, and **car stereos / USB**.
- 📁 **Dedicated Playlist Folders**: Playlists are automatically downloaded into their own folder (`downloads/<Playlist Name>/`), keeping your music library organized without mixing files.
- 🔢 **Preserved Track Ordering**: Adds sequential track numbering (`01 - `, `02 - ...`) so songs play in the original playlist order.
- ⚡ **Batch or Selective Download**: Download all songs in a playlist with a single click, or pick and choose individual tracks with checkboxes.
- 📱 **Mobile Ready (Local Wi-Fi + QR Code)**: Open the web app on your iPhone or Android phone simply by scanning the on-screen QR code!
- 📦 **1-Click ZIP Download**: Download entire playlists as a single `.zip` file on your phone or computer.
- 🖥️ **macOS Integration**: 1-click **"Open in Finder"** to reveal downloaded files immediately.
- 💻 **CLI Downloader Included**: Standalone terminal script for quick command-line downloads.
- 🛡️ **Anti-Throttling**: Built-in Node.js JS challenge solver and EJS integration prevents YouTube signature blocks and throttled speeds.

---

## 🚀 Quick Start

### Option 1: macOS 1-Click Launcher (Easiest)
Simply double-click **`run.command`** in Finder! It will launch the web application and open it in your browser.

---

### Option 2: Terminal / Web App
1. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the launcher:
   ```bash
   ./start.sh
   # Or: streamlit run app.py
   ```
3. Open your browser at `http://localhost:8501`.

---

### Option 3: Terminal Command-Line Downloader (`downloader.py`)
For power users who prefer the terminal:

```bash
# Download single video (default 320 kbps high quality)
python3 downloader.py "https://youtu.be/ZaQqertwNiw"

# Download entire playlist into its own folder:
python3 downloader.py "https://youtube.com/playlist?list=PLsJfa_-ihm2UHcz0JkP3nCnlvI4xwJTAx"

# List playlist tracks without downloading:
python3 downloader.py "https://youtube.com/playlist?list=..." --list

# Custom bitrate (320, 256, 192, 128 kbps):
python3 downloader.py "<URL>" -b 320
```

---

## 📱 How to Use on Your Phone (iPhone & Android)

You can download MP3s directly to your phone without transferring cables!

1. Make sure your **Phone and Mac are connected to the same Wi-Fi**.
2. Run the web app on your Mac.
3. In the sidebar, expand **"📷 Scan QR Code on Phone"** and point your phone's camera at the screen (or enter the displayed IP address, e.g., `http://10.221.67.251:8501`).
4. Paste your YouTube link and tap **Download**:
   - **Single song**: Tap **"📥 Save MP3 to Device / Phone"** to save directly into your phone's **Files / Downloads**.
   - **Full playlist**: Tap **"📦 Download Entire Playlist as ZIP"** to download all songs in one archive!

---

## 📁 How Playlist Organization Works

When you enter a playlist (e.g. *भक्त प्राची बहन चरित्र* with 77 tracks):
1. A new folder is automatically created:
   ```
   downloads/
   └── भक्त प्राची बहन चरित्र (Prachi Behan Charitr)/
       ├── 01 - जब चलाई भगवान श्री कृष्ण ने Baleno Car...mp3
       ├── 02 - जब चलाई भगवान श्री कृष्ण ने Baleno Car (भाग 2)...mp3
       ├── 03 - ...
   ```
2. Inside each MP3:
   - **Album Name** is set to the Playlist Title.
   - **Track Number** is set to `1/77`, `2/77`, etc.
   - **Cover Art** is embedded with the video thumbnail.
3. When you open this folder on any phone or music player, it automatically recognizes it as a **complete album** with the right track order!

---

## ☁️ Cloud Deployment (Access from Anywhere)

If you want to use the app when you are away from home (on cellular data):

### 1. Free Cloud Hosting (Render / Railway / Hugging Face Spaces)
The repository includes a ready-to-deploy **`Dockerfile`**:
1. Push this project to GitHub.
2. In [Render.com](https://render.com) or [Railway.app](https://railway.app), create a new **Web Service** connected to your repo.
3. Select **Docker**. Render will build and deploy it with `ffmpeg` and `nodejs` automatically.
4. You will get a free public HTTPS link (e.g., `https://charcha-mp3.onrender.com`).

### 2. Free Private Mesh (Tailscale)
- Install **Tailscale** on your Mac and Phone (100% free).
- Access your Mac from anywhere on mobile data using your private Tailscale IP with zero port forwarding!

---

## 📦 Project Structure

```
charcha-mp3/
├── app.py              # Streamlit Web App with dark studio UI & mobile QR code
├── core.py             # Core engine (yt-dlp, FFmpeg, ID3v2.3 tagging, ZIP archiving)
├── downloader.py       # Standalone CLI downloader script
├── start.sh            # One-line terminal launch script
├── run.command         # macOS Finder double-clickable launcher
├── Dockerfile          # Production Docker container with ffmpeg & nodejs
├── requirements.txt    # Python package dependencies
├── .gitignore          # Git exclusion rules (keeps media out of git)
└── downloads/          # Downloaded MP3 files and playlist folders
```

---

## 📄 License
MIT License. Created for personal audio downloading and offline listening.
