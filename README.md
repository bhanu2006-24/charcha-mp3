# 🎵 Charcha MP3 — YouTube to MP3 Studio

> **Audio-only YouTube video & full playlist downloader with universal MP3 playback, dedicated playlist folders, two-stage smart resume, embedded album art, and instant mobile phone access.**

---

## ✨ Features

- 🎧 **Pure Audio Extraction**: Downloads high-quality audio with **zero video clutter**.
- 🌟 **Universal Compatibility**: Encoded with **ID3v2.3 tags** (Title, Artist, Album, Track Number, and Embedded Cover Art).
  - Works natively in **Apple Music**, **iOS Files**, **Spotify (Local Files)**, **Android music players (Musicolet, Retro, Poweramp)**, and **car stereos / USB**.
- ⏩ **Two-Stage Smart Resume (Data & Time Saver)**:
  1. **Complete Files**: If an MP3 is already fully downloaded, it is **instantly skipped** (0 MB downloaded, 0 seconds wasted).
  2. **Interrupted / Incomplete Files**: If your download stopped halfway (e.g. Wi-Fi dropped or you closed the app), it **resumes from the exact byte offset** instead of restarting from 0%!
- 📁 **Dedicated Playlist Folders**: Playlists are automatically downloaded into their own folder (`downloads/<Playlist Name>/`), keeping your music library organized without mixing files.
- 🔢 **Preserved Track Ordering**: Adds sequential track numbering (`01 - `, `02 - ...`) so songs play in the original playlist order.
- ⚡ **Batch or Selective Download**: Download all songs in a playlist with a single click, or pick and choose individual tracks with checkboxes.
- 📱 **Mobile Ready (Local Wi-Fi + High-Contrast QR Code)**: Open the web app on your iPhone or Android phone simply by scanning the on-screen QR code!
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
# Download single video (default 320 kbps high quality):
python3 downloader.py "https://youtu.be/ZaQqertwNiw"

# Download playlist into its own folder (skips existing files automatically):
python3 downloader.py "https://youtube.com/playlist?list=PLsJfa_-ihm2UHcz0JkP3nCnlvI4xwJTAx"

# Force re-download / overwrite existing files:
python3 downloader.py "<URL>" --overwrite

# List playlist tracks without downloading:
python3 downloader.py "https://youtube.com/playlist?list=..." --list

# Custom bitrate (320, 256, 192, 128 kbps):
python3 downloader.py "<URL>" -b 320
```

---

## 📱 How to Use on Your Phone (iPhone & Android)

You can download MP3s directly to your phone without transferring cables!

1. Make sure your **Phone and Mac are connected to the same Wi-Fi network**.
2. Run the web app on your Mac.
3. In the sidebar or on the **"📱 Mobile & FAQ Guide"** tab, point your phone camera at the **QR Code** (or enter the displayed IP address, e.g. `http://10.221.67.251:8501` in Safari/Chrome).
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

## ❓ Frequently Asked Questions (FAQ) & Troubleshooting

### 🛑 1. How do I STOP or CLOSE the app?
- **If running in Terminal**: Press **`Ctrl + C`** on your keyboard.
- **If started by double-clicking `run.command`**: Simply close the Terminal window, or press **`Ctrl + C`**.
- **To forcefully kill any running instance in the background**:
  ```bash
  killall streamlit
  # Or find and kill the port:
  lsof -ti :8501 | xargs kill -9
  ```

---

### ⏩ 2. How does Smart Resume work if a download stops halfway?
Charcha MP3 has a **two-stage smart resume**:
- **Stage 1 (Complete Files)**: If an MP3 already exists and is fully downloaded, it is **skipped instantly** (takes 0.01 seconds and consumes 0 MB of internet data).
- **Stage 2 (Incomplete Downloads)**: If a song was 60% downloaded and your internet dropped or you stopped the app, YouTube download resumes **directly from the 60% mark** using HTTP byte-range requests instead of restarting from 0%!
- **Force Re-download**: If you ever want to re-download files, check **"Force re-download / Overwrite"** in the sidebar (or pass `--overwrite` in CLI).

---

### 📶 3. My phone says "Cannot open page" or times out. Why?
1. **Same Wi-Fi Router**: Ensure your phone is connected to the same Wi-Fi router as your Mac (not on cellular 4G/5G).
2. **Check Mac Firewall**:
   - Go to **System Settings > Network > Firewall**.
   - If enabled, click **Options** and allow incoming connections for Python, or temporarily toggle Firewall off.
3. **Guest Wi-Fi / AP Isolation**: Some public or office Wi-Fi networks block devices from talking to each other. Use your home Wi-Fi or turn on Personal Hotspot on your phone and connect your Mac to it.
4. **Tailscale Alternative**: If your router blocks local communication, install **Tailscale** (free) on both your Mac and Phone to access the app securely from anywhere on any connection.

---

### 🎧 4. Will these MP3 files play on any music player or car stereo?
**Yes, 100%!**
- The audio is converted to standard **MP3** with **ID3v2.3 tags** (the most universally supported audio metadata standard in the world).
- **Car Stereos & USB**: Plug a USB flash drive into your car and it will display song names, artists, and cover art.
- **iPhone**: Open in Files app, Apple Music, VLC, or Doppler.
- **Android**: Plays in Samsung Music, Musicolet, Retro Music Player, Poweramp, or Spotify (Local Files).

---

### 🔍 5. Can I download only 5 songs from a 100-song playlist?
**Yes!**
In the Web App, under the playlist preview, select **"Choose specific songs to download"**. An interactive list of all songs will appear with checkboxes, allowing you to select exactly which tracks you want.

---

### 📂 6. Where are my downloaded files stored?
By default, all files are saved in the project's **`downloads/`** directory:
```
/Users/bhanupratapsaini/Coding/Youtube/charcha-mp3/downloads/
```
In the Web App, simply click **"📂 Open Downloads in Finder"** to view them immediately in macOS Finder.

---

### 🔄 7. What if YouTube changes its format or a download fails?
YouTube occasionally updates its internal streaming protocols. To ensure you always have the latest format extractors, upgrade `yt-dlp`:
```bash
pip install --upgrade yt-dlp
```

---

### ☁️ 8. How can I deploy this to use it when away from home?
The repository includes a ready-to-deploy **`Dockerfile`**:
1. Push this project to GitHub.
2. Connect your repository to **Render.com** or **Railway.app** (Select **Web Service > Docker**).
3. It will deploy a 24/7 web app with `ffmpeg` and `nodejs` preinstalled and give you a free public HTTPS address (e.g. `https://charcha-mp3.onrender.com`).

---

## 📦 Project Structure

```
charcha-mp3/
├── app.py              # Streamlit Web App with dark studio UI, QR code & Smart Resume
├── core.py             # Core engine (yt-dlp, FFmpeg, ID3v2.3 tagging, ZIP archiving, Resume)
├── downloader.py       # Standalone CLI downloader script
├── start.sh            # Terminal launch script
├── run.command         # macOS Finder double-clickable launcher
├── Dockerfile          # Production Docker container with ffmpeg & nodejs
├── requirements.txt    # Python package dependencies
├── .gitignore          # Git exclusion rules (keeps media out of git)
└── downloads/          # Downloaded MP3 files and dedicated playlist folders
```

---

## 📄 License
MIT License. Created for personal audio downloading and offline listening.
