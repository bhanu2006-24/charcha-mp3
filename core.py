import os
import re
import io
import time
import socket
import shutil
import base64
import zipfile
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import qrcode
from PIL import Image
import mutagen
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TRCK, ID3NoHeaderError
import yt_dlp

DEFAULT_DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "downloads"))

def get_ffmpeg_path() -> Optional[str]:
    """Find the path to ffmpeg executable."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    common_paths = [
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]
    for p in common_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return None

def get_node_path() -> Optional[str]:
    """Find node path for solving YouTube JS challenges."""
    found = shutil.which("node")
    if found:
        return found
    common_paths = [
        "/opt/homebrew/bin/node",
        "/usr/local/bin/node",
        "/usr/bin/node",
    ]
    for p in common_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return None

def get_local_ip() -> str:
    """Get the local network IP address for mobile phone access on Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass
    try:
        cmd = "ipconfig getifaddr en0 || ipconfig getifaddr en1"
        out = subprocess.check_output(cmd, shell=True).decode().strip()
        if out:
            return out
    except Exception:
        pass
    return "127.0.0.1"

def generate_qr_code(data: str) -> Image.Image:
    """Generate a clean QR code PIL Image for the given URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#10b981", back_color="#0f172a")
    return img

def sanitize_filename(name: str) -> str:
    """Clean filename of characters that are invalid on Mac/Windows/Linux/Android."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned or "audio_track"

def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds into HH:MM:SS or MM:SS."""
    if not seconds:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def format_bytes(num_bytes: Optional[int]) -> str:
    """Format byte size into human readable string."""
    if not num_bytes:
        return "0 KB"
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"

def get_base_ydl_opts(quiet: bool = True) -> Dict[str, Any]:
    """Base options for yt-dlp including JS runtimes and ffmpeg."""
    ffmpeg_bin = get_ffmpeg_path()
    node_bin = get_node_path()

    opts: Dict[str, Any] = {
        "quiet": quiet,
        "no_warnings": quiet,
        "ignoreerrors": True,
        "remote_components": ["ejs:github"],
    }
    if ffmpeg_bin:
        opts["ffmpeg_location"] = ffmpeg_bin
    if node_bin:
        opts["js_runtimes"] = {"node": {"path": node_bin}}
    return opts

def tag_mp3_file(
    filepath: str,
    title: str,
    artist: str,
    album: Optional[str] = None,
    track_number: Optional[int] = None,
    total_tracks: Optional[int] = None,
    thumbnail_url: Optional[str] = None
):
    """
    Ensure ID3v2.3 tags (Title, Artist, Album, Track number, Cover Art)
    are permanently embedded for maximum universal playback on iOS, Android, Car stereos, and Mac.
    """
    if not filepath or not os.path.exists(filepath):
        return

    try:
        try:
            tags = ID3(filepath)
        except ID3NoHeaderError:
            tags = ID3()

        # Set text tags (v2.3 compatible)
        tags.add(TIT2(encoding=3, text=title))
        tags.add(TPE1(encoding=3, text=artist))
        if album:
            tags.add(TALB(encoding=3, text=album))
        if track_number is not None:
            trck_str = f"{track_number}/{total_tracks}" if total_tracks else str(track_number)
            tags.add(TRCK(encoding=3, text=trck_str))

        # Check if cover art exists; if not and thumbnail_url is present, fetch and embed it
        has_cover = any(isinstance(f, APIC) for f in tags.values())
        if not has_cover and thumbnail_url:
            try:
                req = urllib.request.Request(
                    thumbnail_url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    art_data = resp.read()
                    tags.add(APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3, # front cover
                        desc="Cover",
                        data=art_data
                    ))
            except Exception:
                pass

        # Save with ID3v2.3 standard (the most universally supported format)
        tags.save(filepath, v2_version=3)
    except Exception:
        pass

def inspect_url(url: str) -> Dict[str, Any]:
    """
    Inspect a URL to determine if it is a single video or a playlist,
    and extract metadata without downloading media.
    """
    opts = get_base_ydl_opts(quiet=True)
    opts.update({
        "extract_flat": "in_playlist",
        "skip_download": True,
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            raise ValueError("Could not fetch information from this YouTube URL. Please verify the link.")

        is_playlist = info.get("_type") == "playlist" or "entries" in info

        if is_playlist:
            raw_entries = list(info.get("entries", []))
            tracks = []
            for i, entry in enumerate(raw_entries):
                if not entry:
                    continue
                tracks.append({
                    "index": i + 1,
                    "id": entry.get("id"),
                    "title": entry.get("title") or f"Track {i+1}",
                    "url": entry.get("url") if entry.get("url", "").startswith("http") else f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "duration": format_duration(entry.get("duration")),
                    "duration_sec": entry.get("duration") or 0,
                    "uploader": entry.get("uploader") or entry.get("channel") or info.get("uploader") or "Various Artists",
                    "thumbnail": entry.get("thumbnail") or (entry.get("thumbnails", [{}])[-1].get("url") if entry.get("thumbnails") else None)
                })

            thumb = info.get("thumbnail")
            if not thumb and tracks and tracks[0].get("thumbnail"):
                thumb = tracks[0]["thumbnail"]

            return {
                "type": "playlist",
                "title": info.get("title") or "YouTube Playlist",
                "uploader": info.get("uploader") or info.get("channel") or "Various Artists",
                "track_count": len(tracks),
                "thumbnail": thumb,
                "tracks": tracks,
                "original_url": url,
            }
        else:
            thumb = info.get("thumbnail")
            if not thumb and info.get("thumbnails"):
                thumb = info["thumbnails"][-1].get("url")

            return {
                "type": "video",
                "id": info.get("id"),
                "title": info.get("title") or "YouTube Track",
                "uploader": info.get("uploader") or info.get("channel") or "Unknown Artist",
                "duration": format_duration(info.get("duration")),
                "duration_sec": info.get("duration") or 0,
                "thumbnail": thumb,
                "view_count": info.get("view_count"),
                "original_url": url,
            }

def download_track(
    url: str,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    filename_prefix: str = "",
    bitrate: str = "320",
    album_name: Optional[str] = None,
    track_number: Optional[int] = None,
    total_tracks: Optional[int] = None,
    embed_thumbnail: bool = True,
    embed_metadata: bool = True,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Downloads a single video audio track and converts to high-quality universally playable MP3.
    """
    os.makedirs(output_dir, exist_ok=True)
    opts = get_base_ydl_opts(quiet=True)

    prefix = f"{filename_prefix} - " if filename_prefix else ""
    out_template = os.path.join(output_dir, f"{prefix}%(title)s.%(ext)s")

    postprocessors = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": str(bitrate),
        }
    ]

    if embed_metadata:
        postprocessors.append({"key": "FFmpegMetadata"})

    if embed_thumbnail:
        opts["writethumbnail"] = True
        postprocessors.append({"key": "EmbedThumbnail"})

    downloaded_files: List[str] = []

    def ydl_progress_hook(d: Dict[str, Any]):
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            pct = (downloaded / total * 100) if total > 0 else 0
            speed = d.get("speed") or 0
            eta = d.get("eta") or 0
            if progress_callback:
                progress_callback({
                    "status": "downloading",
                    "percent": pct,
                    "downloaded_bytes": downloaded,
                    "total_bytes": total,
                    "speed_str": f"{format_bytes(speed)}/s" if speed else "Calculating...",
                    "eta_str": f"{eta}s" if eta else "--",
                })
        elif status == "finished":
            filename = d.get("filename")
            if filename:
                mp3_guess = os.path.splitext(filename)[0] + ".mp3"
                downloaded_files.append(mp3_guess)
            if progress_callback:
                progress_callback({
                    "status": "converting",
                    "percent": 99.0,
                    "message": "Converting to MP3 & embedding metadata/cover art...",
                })

    opts.update({
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "postprocessors": postprocessors,
        "postprocessor_args": {
            "ffmpeg": ["-id3v2_version", "3"]
        },
        "progress_hooks": [ydl_progress_hook],
        "noplaylist": True,
    })

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title") or "Audio"
            artist = info.get("uploader") or info.get("channel") or "Unknown Artist"
            thumbnail = info.get("thumbnail")

            # Determine final file path
            final_mp3 = None
            if downloaded_files and os.path.exists(downloaded_files[0]):
                final_mp3 = downloaded_files[0]
            else:
                mp3_files = sorted(
                    Path(output_dir).glob("*.mp3"),
                    key=os.path.getmtime,
                    reverse=True
                )
                if mp3_files:
                    final_mp3 = str(mp3_files[0])

            # Ensure ID3v2.3 tags are clean and universal for all music players
            if final_mp3 and os.path.exists(final_mp3):
                tag_mp3_file(
                    filepath=final_mp3,
                    title=title,
                    artist=artist,
                    album=album_name or (artist + " Audio"),
                    track_number=track_number,
                    total_tracks=total_tracks,
                    thumbnail_url=thumbnail,
                )

            # Cleanup stray non-mp3 intermediate files
            for ext in [".webm", ".m4a", ".webp", ".jpg", ".part", ".ytdl"]:
                for stray in Path(output_dir).glob(f"*{ext}"):
                    try:
                        os.remove(stray)
                    except Exception:
                        pass

            filesize = os.path.getsize(final_mp3) if final_mp3 and os.path.exists(final_mp3) else 0

            return {
                "success": True,
                "title": title,
                "filepath": final_mp3,
                "filesize": filesize,
                "filesize_str": format_bytes(filesize),
                "duration": format_duration(info.get("duration")),
                "uploader": artist,
                "thumbnail": thumbnail,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filepath": None,
        }

def download_playlist(
    playlist_info: Dict[str, Any],
    selected_indices: Optional[List[int]] = None,
    output_dir: str = DEFAULT_DOWNLOAD_DIR,
    subfolder_per_playlist: bool = True,
    add_track_numbers: bool = True,
    bitrate: str = "320",
    embed_thumbnail: bool = True,
    overall_progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Downloads selected tracks from a playlist into high quality MP3s inside a dedicated folder.
    """
    playlist_title = playlist_info.get("title") or "Playlist"
    tracks = playlist_info.get("tracks", [])

    if selected_indices is not None:
        target_tracks = [t for t in tracks if t["index"] in selected_indices]
    else:
        target_tracks = tracks

    target_dir = output_dir
    if subfolder_per_playlist:
        safe_folder = sanitize_filename(playlist_title)
        target_dir = os.path.join(output_dir, safe_folder)
    os.makedirs(target_dir, exist_ok=True)

    total_count = len(target_tracks)
    downloaded_tracks = []
    failed_tracks = []

    for idx, track in enumerate(target_tracks):
        prefix = f"{track['index']:02d}" if add_track_numbers else ""
        track_title = track.get("title") or f"Track {idx+1}"

        if overall_progress_callback:
            overall_progress_callback({
                "current_index": idx + 1,
                "total_count": total_count,
                "track_title": track_title,
                "status": "starting",
                "percent": (idx / total_count) * 100,
            })

        def track_sub_progress(d: Dict[str, Any]):
            if overall_progress_callback:
                overall_progress_callback({
                    "current_index": idx + 1,
                    "total_count": total_count,
                    "track_title": track_title,
                    "status": d.get("status"),
                    "percent": ((idx + (d.get("percent", 0) / 100)) / total_count) * 100,
                    "speed_str": d.get("speed_str", ""),
                    "eta_str": d.get("eta_str", ""),
                })

        res = download_track(
            url=track["url"],
            output_dir=target_dir,
            filename_prefix=prefix,
            bitrate=bitrate,
            album_name=playlist_title,
            track_number=track["index"],
            total_tracks=len(tracks),
            embed_thumbnail=embed_thumbnail,
            progress_callback=track_sub_progress,
        )

        if res.get("success") and res.get("filepath"):
            downloaded_tracks.append(res)
        else:
            failed_tracks.append({
                "index": track["index"],
                "title": track_title,
                "error": res.get("error", "Unknown error"),
            })

    if overall_progress_callback:
        overall_progress_callback({
            "current_index": total_count,
            "total_count": total_count,
            "track_title": "All selected tracks processed",
            "status": "completed",
            "percent": 100.0,
        })

    return {
        "success": len(downloaded_tracks) > 0,
        "total_requested": total_count,
        "total_succeeded": len(downloaded_tracks),
        "total_failed": len(failed_tracks),
        "downloaded_tracks": downloaded_tracks,
        "failed_tracks": failed_tracks,
        "target_dir": target_dir,
        "playlist_title": playlist_title,
    }

def create_zip_archive(files: List[str], zip_filename: str = "charcha_playlist_mp3.zip") -> str:
    """
    Bundles the given list of files into a zip archive inside the downloads directory.
    Returns the path to the zip file.
    """
    zip_path = os.path.join(DEFAULT_DOWNLOAD_DIR, zip_filename)
    os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            if f and os.path.exists(f):
                zf.write(f, arcname=os.path.basename(f))
    return zip_path

def reveal_in_finder(filepath: str) -> bool:
    """Reveal file or folder in macOS Finder."""
    try:
        if os.path.isfile(filepath):
            subprocess.run(["open", "-R", filepath], check=True)
        else:
            subprocess.run(["open", filepath], check=True)
        return True
    except Exception:
        return False

def list_downloaded_mp3s(directory: str = DEFAULT_DOWNLOAD_DIR) -> List[Dict[str, Any]]:
    """Scan and list all MP3 files in the downloads directory."""
    if not os.path.exists(directory):
        return []
    results = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(".mp3"):
                full_path = os.path.join(root, f)
                try:
                    stat = os.stat(full_path)
                    results.append({
                        "name": f,
                        "path": full_path,
                        "rel_folder": os.path.relpath(root, directory),
                        "size": stat.st_size,
                        "size_str": format_bytes(stat.st_size),
                        "mtime": stat.st_mtime,
                        "mtime_str": time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime)),
                    })
                except Exception:
                    continue
    # Sort newest first
    results.sort(key=lambda x: x["mtime"], reverse=True)
    return results
