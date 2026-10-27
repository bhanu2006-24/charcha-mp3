#!/usr/bin/env python3
"""
Charcha MP3 - YouTube to MP3 CLI Downloader
Download YouTube videos or full playlists directly to MP3.

Features:
  - Smart Resume: Skips already completed MP3s
  - Partial Resume: Continues interrupted downloads from byte offset
  - Dedicated Playlist Folders & Ordered Track Numbering

Usage:
    python3 downloader.py "<YouTube URL>" [options]

Examples:
    python3 downloader.py "https://youtu.be/ZaQqertwNiw"
    python3 downloader.py "https://youtube.com/playlist?list=..." -b 320
    python3 downloader.py "https://youtube.com/playlist?list=..." --overwrite
    python3 downloader.py "https://youtube.com/playlist?list=..." --list
"""

import sys
import argparse
import core

def main():
    parser = argparse.ArgumentParser(
        description="🎵 Charcha MP3 - High Quality YouTube Video & Playlist MP3 Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", help="YouTube video or playlist URL")
    parser.add_argument(
        "-b", "--bitrate",
        choices=["320", "256", "192", "128"],
        default="320",
        help="MP3 audio bitrate (default: 320 kbps)"
    )
    parser.add_argument(
        "-o", "--output",
        default=core.DEFAULT_DOWNLOAD_DIR,
        help=f"Download folder (default: {core.DEFAULT_DOWNLOAD_DIR})"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Force re-download and overwrite existing files (disables smart skip)"
    )
    parser.add_argument(
        "--no-art",
        action="store_true",
        help="Do not embed video thumbnail artwork into MP3"
    )
    parser.add_argument(
        "--no-prefix",
        action="store_true",
        help="Do not prepend track numbers to playlist filenames"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="Inspect URL and list playlist tracks without downloading"
    )

    args = parser.parse_args()

    print("\n🔍 Inspecting URL...")
    try:
        info = core.inspect_url(args.url)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    is_playlist = info.get("type") == "playlist"

    if is_playlist:
        print(f"\n📂 Playlist: {info.get('title')}")
        print(f"👤 Channel:  {info.get('uploader')}")
        print(f"🎶 Tracks:   {info.get('track_count')}")

        if args.list:
            print("\nTracklist:")
            for t in info.get("tracks", []):
                print(f"  [{t['index']:02d}] {t['title']} ({t['duration']})")
            return

        confirm = input(f"\n🚀 Download all {info.get('track_count')} tracks in {args.bitrate}k MP3? [Y/n]: ").strip().lower()
        if confirm and confirm not in ("y", "yes"):
            print("Download cancelled.")
            return

        print(f"\n📥 Target folder: {args.output}")
        if not args.overwrite:
            print("⏩ Smart Resume active: Existing files will be skipped; incomplete files will resume.")

        def playlist_progress(d):
            status = d.get("status")
            idx = d.get("current_index", 1)
            total = d.get("total_count", 1)
            pct = d.get("percent", 0.0)
            title = d.get("track_title", "")
            speed = d.get("speed_str", "")
            eta = d.get("eta_str", "")
            msg = d.get("message", "")

            if status == "starting":
                print(f"\n[{idx}/{total}] Checking: {title}")
            elif status == "skipped":
                print(f"  ⏩ {msg}")
            elif status == "resuming":
                print(f"  🔄 {msg}")
            elif status == "downloading":
                print(f"  Downloading... {pct:.1f}% | {speed} | ETA: {eta}", end="\r")
            elif status == "converting":
                print("  Converting to MP3 & embedding tags...", end="\r")

        res = core.download_playlist(
            playlist_info=info,
            output_dir=args.output,
            subfolder_per_playlist=True,
            add_track_numbers=not args.no_prefix,
            bitrate=args.bitrate,
            embed_thumbnail=not args.no_art,
            overwrite_existing=args.overwrite,
            overall_progress_callback=playlist_progress,
        )

        print("\n\n" + "=" * 55)
        print(f"✅ Playlist processing complete!")
        print(f"   Total in playlist: {res['total_requested']}")
        print(f"   Newly downloaded:  {res.get('total_new', 0)}")
        print(f"   Resumed partial:   {res.get('total_resumed', 0)}")
        print(f"   Skipped existing:  {res.get('total_skipped', 0)}")
        if res.get('total_failed', 0) > 0:
            print(f"   Failed:            {res['total_failed']}")
        print(f"   Saved in folder:   {res['target_dir']}")
        print("=" * 55)

        if sys.platform == "darwin":
            core.reveal_in_finder(res['target_dir'])

    else:
        print(f"\n🎵 Video:    {info.get('title')}")
        print(f"👤 Channel:  {info.get('uploader')}")
        print(f"⏱️  Duration: {info.get('duration')}")

        def track_progress(d):
            status = d.get("status")
            if status == "skipped":
                print(f"  ⏩ {d.get('message')}")
            elif status == "resuming":
                print(f"  🔄 {d.get('message')}")
            elif status == "downloading":
                pct = d.get("percent", 0.0)
                speed = d.get("speed_str", "")
                eta = d.get("eta_str", "")
                print(f"  Downloading: {pct:.1f}% | {speed} | ETA: {eta}", end="\r")
            elif status == "converting":
                print("\n  Converting to MP3 & embedding tags...", end="\r")

        print(f"\n📥 Processing {args.bitrate}k MP3...")
        res = core.download_track(
            url=args.url,
            output_dir=args.output,
            bitrate=args.bitrate,
            embed_thumbnail=not args.no_art,
            overwrite=args.overwrite,
            expected_title=info.get("title"),
            progress_callback=track_progress,
        )

        if res.get("success"):
            print("\n\n" + "=" * 55)
            if res.get("was_skipped"):
                print("⏩ File was already downloaded! Re-used existing MP3.")
            elif res.get("was_resumed"):
                print("🔄 Resumed from previously interrupted download and completed!")
            else:
                print("✅ Download successful!")
            print(f"   Title: {res.get('title')}")
            print(f"   File:  {res.get('filepath')}")
            print(f"   Size:  {res.get('filesize_str')}")
            print("=" * 55)
            if sys.platform == "darwin" and res.get("filepath"):
                core.reveal_in_finder(res.get("filepath"))
        else:
            print(f"\n❌ Download failed: {res.get('error')}")
            sys.exit(1)

if __name__ == "__main__":
    main()
