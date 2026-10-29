#!/usr/bin/env python3
"""
Batch Downloader for Charcha MP3
Reads list.txt and downloads all playlists and single audio tracks directly to MP3.
Reports any videos or playlists that fail to download.
Does NOT generate zip archives to conserve storage space.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List
import core

def load_urls(list_file: str) -> List[str]:
    if not os.path.exists(list_file):
        print(f"❌ Error: File '{list_file}' not found. Please create it or copy from list.txt.example")
        sys.exit(1)
        
    urls = []
    with open(list_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and ("youtube.com" in line or "youtu.be" in line):
                urls.append(line)
    return urls

def main():
    parser = argparse.ArgumentParser(description="Charcha MP3 - Batch Downloader")
    parser.add_argument(
        "-b", "--bitrate",
        choices=["128", "192", "256", "320"],
        default="128",
        help="MP3 audio bitrate (default: 128 kbps)"
    )
    args = parser.parse_args()
    selected_bitrate = args.bitrate

    list_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "list.txt"))
    urls = load_urls(list_path)
    
    print("=" * 65)
    print("🎵 Charcha MP3 - Batch Downloader")
    print(f"📄 Found {len(urls)} entries to process in list.txt")
    print(f"📁 Output Directory: {core.DEFAULT_DOWNLOAD_DIR}")
    print(f"🎚️ Audio Bitrate: {selected_bitrate} kbps")
    print(f"📦 ZIP Archive: Disabled (saving storage)")
    print("=" * 65)

    report: Dict[str, Any] = {
        "total_entries": len(urls),
        "successful_tracks": [],
        "skipped_tracks": [],
        "failed_items": [],
        "playlists_processed": [],
    }

    start_time = time.time()

    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] 🔍 Checking: {url}")
        try:
            info = core.inspect_url(url)
        except Exception as e:
            print(f"  ❌ Failed to inspect URL: {e}")
            report["failed_items"].append({
                "url": url,
                "title": "Unknown (Failed to inspect)",
                "type": "unknown",
                "error": str(e)
            })
            continue

        item_type = info.get("type")

        if item_type == "playlist":
            playlist_title = info.get("title", "Unknown Playlist")
            track_count = info.get("track_count", 0)
            print(f"  📂 Playlist: {playlist_title} ({track_count} tracks)")

            def pl_callback(d):
                st = d.get("status")
                c_idx = d.get("current_index", 1)
                t_count = d.get("total_count", 1)
                title = d.get("track_title", "")
                speed = d.get("speed_str", "")
                pct = d.get("percent", 0.0)
                eta = d.get("eta_str", "")
                msg = d.get("message", "")

                if st == "starting":
                    print(f"    [{c_idx}/{t_count}] Starting: {title}")
                elif st == "skipped":
                    print(f"      ⏩ Skipped: {msg}")
                elif st == "resuming":
                    print(f"      🔄 Resuming: {msg}")
                elif st == "downloading":
                    print(f"      Downloading {pct:.1f}% | {speed} | ETA: {eta}    ", end="\r")
                elif st == "converting":
                    print(f"      Converting to MP3 & tagging...                  ", end="\r")

            try:
                res = core.download_playlist(
                    playlist_info=info,
                    output_dir=core.DEFAULT_DOWNLOAD_DIR,
                    subfolder_per_playlist=True,
                    add_track_numbers=True,
                    bitrate=selected_bitrate,
                    embed_thumbnail=True,
                    overwrite_existing=False,
                    overall_progress_callback=pl_callback,
                )

                report["playlists_processed"].append({
                    "title": playlist_title,
                    "url": url,
                    "total_tracks": res.get("total_requested", 0),
                    "new_downloaded": res.get("total_new", 0),
                    "skipped": res.get("total_skipped", 0),
                    "resumed": res.get("total_resumed", 0),
                    "failed": res.get("total_failed", 0),
                    "folder": res.get("target_dir", "")
                })

                for t in res.get("downloaded_tracks", []):
                    if t.get("was_skipped"):
                        report["skipped_tracks"].append({
                            "title": t.get("title"),
                            "file": t.get("filepath"),
                            "playlist": playlist_title
                        })
                    else:
                        report["successful_tracks"].append({
                            "title": t.get("title"),
                            "file": t.get("filepath"),
                            "filesize": t.get("filesize_str"),
                            "playlist": playlist_title
                        })

                for f in res.get("failed_tracks", []):
                    print(f"\n    ❌ Track failed in playlist: {f.get('title')} ({f.get('error')})")
                    report["failed_items"].append({
                        "url": url,
                        "title": f.get("title"),
                        "type": "playlist_track",
                        "playlist": playlist_title,
                        "track_index": f.get("index"),
                        "error": str(f.get("error"))
                    })

                print(f"\n  ✅ Playlist done: {res.get('total_succeeded', 0)} succeeded ({res.get('total_new', 0)} new, {res.get('total_skipped', 0)} skipped), {res.get('total_failed', 0)} failed.")

            except Exception as e:
                print(f"  ❌ Playlist download crashed: {e}")
                report["failed_items"].append({
                    "url": url,
                    "title": playlist_title,
                    "type": "playlist",
                    "error": str(e)
                })

        else: # Single video
            video_title = info.get("title", "Unknown Video")
            print(f"  🎵 Video: {video_title}")

            def track_callback(d):
                st = d.get("status")
                if st == "downloading":
                    pct = d.get("percent", 0.0)
                    speed = d.get("speed_str", "")
                    eta = d.get("eta_str", "")
                    print(f"    Downloading {pct:.1f}% | {speed} | ETA: {eta}    ", end="\r")
                elif st == "converting":
                    print(f"    Converting to MP3 & tagging...                  ", end="\r")

            try:
                res = core.download_track(
                    url=url,
                    output_dir=core.DEFAULT_DOWNLOAD_DIR,
                    bitrate=selected_bitrate,
                    embed_thumbnail=True,
                    overwrite=False,
                    expected_title=video_title,
                    progress_callback=track_callback,
                )

                if res.get("success") and res.get("filepath"):
                    if res.get("was_skipped"):
                        print(f"\n    ⏩ Already downloaded: {os.path.basename(res['filepath'])}")
                        report["skipped_tracks"].append({
                            "title": video_title,
                            "url": url,
                            "file": res.get("filepath")
                        })
                    else:
                        print(f"\n    ✅ Downloaded: {os.path.basename(res['filepath'])} ({res.get('filesize_str')})")
                        report["successful_tracks"].append({
                            "title": video_title,
                            "url": url,
                            "file": res.get("filepath"),
                            "filesize": res.get("filesize_str")
                        })
                else:
                    err = res.get("error", "Unknown error")
                    print(f"\n    ❌ Failed: {err}")
                    report["failed_items"].append({
                        "url": url,
                        "title": video_title,
                        "type": "video",
                        "error": err
                    })

            except Exception as e:
                print(f"\n    ❌ Download crashed: {e}")
                report["failed_items"].append({
                    "url": url,
                    "title": video_title,
                    "type": "video",
                    "error": str(e)
                })

    elapsed = time.time() - start_time
    report["elapsed_seconds"] = round(elapsed, 1)

    # Save report
    report_path = os.path.join(os.path.dirname(__file__), "download_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 65)
    print("🏁 Batch Download Complete!")
    print(f"⏱️  Time Elapsed: {core.format_duration(int(elapsed))}")
    print(f"✅ Newly Downloaded: {len(report['successful_tracks'])} tracks")
    print(f"⏩ Skipped (already downloaded): {len(report['skipped_tracks'])} tracks")
    print(f"❌ Failed Items: {len(report['failed_items'])}")
    if report["failed_items"]:
        print("\nFailed Items List:")
        for idx, fi in enumerate(report["failed_items"], 1):
            print(f"  {idx}. [{fi.get('type')}] {fi.get('title')} ({fi.get('url')}): {fi.get('error')}")
    print("=" * 65)
    print(f"📄 Detailed report saved to: {report_path}")

if __name__ == "__main__":
    main()
