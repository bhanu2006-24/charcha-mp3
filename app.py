import os
import io
import time
import core
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Charcha MP3 - YouTube Audio Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background and containers */
    .stApp {
        background: radial-gradient(circle at 15% 20%, #111827 0%, #030712 100%);
        color: #f3f4f6;
    }

    /* Custom Header Banner */
    .hero-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(16px);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
    }

    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa 0%, #38bdf8 50%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
    }

    /* Badges */
    .badge-playlist {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    .badge-video {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-block;
    }

    /* Mobile QR Box */
    .phone-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px dashed rgba(52, 211, 153, 0.4);
        border-radius: 14px;
        padding: 14px 18px;
        color: #e2e8f0;
        font-size: 0.88rem;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        padding: 8px 20px;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 12px;
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #f8fafc !important;
        font-size: 0.95rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.25) !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #a78bfa, #38bdf8, #34d399);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "inspected_url" not in st.session_state:
    st.session_state.inspected_url = ""
if "url_info" not in st.session_state:
    st.session_state.url_info = None
if "last_download" not in st.session_state:
    st.session_state.last_download = None

local_ip = core.get_local_ip()
phone_url = f"http://{local_ip}:8501"

# Sidebar: Controls & Info
with st.sidebar:
    st.markdown("### 🎛️ Audio Settings")
    bitrate = st.selectbox(
        "MP3 Bitrate (Audio Quality)",
        options=["320", "256", "192", "128"],
        index=0,
        help="320 kbps gives the cleanest, highest studio master audio quality."
    )
    embed_art = st.checkbox(
        "Embed Album Cover Art",
        value=True,
        help="Embeds the YouTube thumbnail directly into the MP3 file tags (shows on lockscreen & Apple Music)."
    )
    
    st.markdown("---")
    st.markdown("### 📁 Downloads Folder")
    st.code(core.DEFAULT_DOWNLOAD_DIR, language="text")
    
    if st.button("📂 Open Downloads in Finder", use_container_width=True):
        if not os.path.exists(core.DEFAULT_DOWNLOAD_DIR):
            os.makedirs(core.DEFAULT_DOWNLOAD_DIR, exist_ok=True)
        core.reveal_in_finder(core.DEFAULT_DOWNLOAD_DIR)
        st.toast("Opened in Finder!")

    st.markdown("---")
    st.markdown("### 📱 Mobile Access")
    st.markdown(f"Access on your phone on the same Wi-Fi:")
    st.code(phone_url, language="text")
    
    with st.expander("📷 Scan QR Code on Phone", expanded=False):
        try:
            qr_img = core.generate_qr_code(phone_url)
            st.image(qr_img, caption="Point iPhone/Android camera to open", use_container_width=True)
        except Exception:
            pass

    st.markdown("---")
    st.caption("⚡ Powered by yt-dlp & FFmpeg")

# Main Header Banner
st.markdown(f"""
<div class="hero-header">
    <div>
        <h1 class="hero-title">🎵 Charcha MP3</h1>
        <p class="hero-subtitle">Studio-Grade YouTube Video & Full Playlist MP3 Downloader</p>
    </div>
    <div>
        <span class="badge-success">● System Ready</span>
        <span class="badge-playlist">⚡ 320k Master</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_download, tab_library, tab_guide = st.tabs(["⚡ Downloader", "📚 My MP3 Library", "📱 Mobile & Deploy Guide"])

# TAB 1: DOWNLOADER
with tab_download:
    st.markdown("#### 🔗 Enter YouTube Video or Playlist URL")
    
    col_input, col_inspect = st.columns([5, 1])
    with col_input:
        url_input = st.text_input(
            "YouTube URL",
            placeholder="Paste YouTube video or playlist link (e.g., https://youtube.com/playlist?list=...)",
            label_visibility="collapsed"
        )
    with col_inspect:
        inspect_btn = st.button("🔍 Inspect", type="primary", use_container_width=True)

    # Quick sample buttons
    sample_col1, sample_col2, sample_col3 = st.columns([1.5, 1.5, 2.5])
    with sample_col1:
        if st.button("📌 Load Sample Video", use_container_width=True):
            st.session_state.inspected_url = "https://youtu.be/ZaQqertwNiw"
            with st.spinner("Inspecting video..."):
                try:
                    st.session_state.url_info = core.inspect_url(st.session_state.inspected_url)
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()
    with sample_col2:
        if st.button("📂 Load Sample Playlist", use_container_width=True):
            st.session_state.inspected_url = "https://youtube.com/playlist?list=PLsJfa_-ihm2UHcz0JkP3nCnlvI4xwJTAx&si=F2R6rnoaUinWmmMH"
            with st.spinner("Inspecting playlist..."):
                try:
                    st.session_state.url_info = core.inspect_url(st.session_state.inspected_url)
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()

    # Trigger inspection on button click or change
    if inspect_btn and url_input.strip():
        st.session_state.inspected_url = url_input.strip()
        with st.spinner("🔍 Fetching metadata from YouTube..."):
            try:
                st.session_state.url_info = core.inspect_url(url_input.strip())
            except Exception as e:
                st.session_state.url_info = None
                st.error(f"Failed to inspect URL: {e}")

    info = st.session_state.url_info

    if info:
        is_playlist = info.get("type") == "playlist"
        
        st.markdown("<hr style='margin: 20px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
        
        # PREVIEW CARD
        preview_col1, preview_col2 = st.columns([1, 2.5])
        with preview_col1:
            thumb = info.get("thumbnail")
            if thumb:
                st.image(thumb, use_container_width=True)
            else:
                st.markdown("<div style='height: 140px; background: #1e293b; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 2rem;'>🎵</div>", unsafe_allow_html=True)

        with preview_col2:
            if is_playlist:
                st.markdown(f"<span class='badge-playlist'>📁 FULL PLAYLIST ({info.get('track_count')} TRACKS)</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge-video'>📺 SINGLE VIDEO</span>", unsafe_allow_html=True)

            st.markdown(f"### {info.get('title')}")
            st.markdown(f"**Channel / Artist:** `{info.get('uploader')}`")
            if not is_playlist:
                st.markdown(f"**Duration:** `{info.get('duration')}`")
            else:
                st.markdown(f"**Total Songs:** `{info.get('track_count')}` songs")

        # =========================================================
        # SINGLE VIDEO DOWNLOAD WORKFLOW
        # =========================================================
        if not is_playlist:
            st.markdown("### 📥 Download Options")
            st.info(f"Target format: **MP3** ({bitrate} kbps) with **embedded cover art & metadata**.")
            
            dl_btn = st.button("🚀 Download MP3 Now", type="primary", use_container_width=True)
            
            if dl_btn:
                progress_bar = st.progress(0.0)
                status_text = st.empty()
                speed_text = st.empty()

                def update_progress(d):
                    status = d.get("status")
                    if status == "downloading":
                        pct = d.get("percent", 0.0)
                        progress_bar.progress(min(max(pct / 100.0, 0.0), 1.0))
                        status_text.markdown(f"📥 Downloading audio stream... **{pct:.1f}%**")
                        speed_text.caption(f"Speed: {d.get('speed_str', '')} | ETA: {d.get('eta_str', '')}")
                    elif status == "converting":
                        progress_bar.progress(0.95)
                        status_text.markdown("🔄 **Converting to high-quality MP3 & embedding cover art...**")
                        speed_text.caption("Finalizing tags...")

                with st.spinner("Processing..."):
                    res = core.download_track(
                        url=info["original_url"],
                        output_dir=core.DEFAULT_DOWNLOAD_DIR,
                        bitrate=bitrate,
                        embed_thumbnail=embed_art,
                        progress_callback=update_progress,
                    )

                if res.get("success"):
                    progress_bar.progress(1.0)
                    status_text.empty()
                    speed_text.empty()
                    st.success(f"🎉 Successfully downloaded: **{res.get('title')}**")
                    
                    st.session_state.last_download = res

                    # Show player & download buttons
                    filepath = res.get("filepath")
                    if filepath and os.path.exists(filepath):
                        # In-browser audio player
                        with open(filepath, "rb") as f:
                            audio_bytes = f.read()
                        
                        st.markdown("#### 🎧 Listen Preview")
                        st.audio(audio_bytes, format="audio/mp3")

                        action_c1, action_c2 = st.columns(2)
                        with action_c1:
                            st.download_button(
                                label="📥 Save MP3 to Device / Phone",
                                data=audio_bytes,
                                file_name=os.path.basename(filepath),
                                mime="audio/mpeg",
                                use_container_width=True,
                                type="primary"
                            )
                        with action_c2:
                            if st.button("📂 Reveal in Finder", use_container_width=True):
                                core.reveal_in_finder(filepath)
                                st.toast("Highlighted file in Finder!")
                else:
                    st.error(f"❌ Download failed: {res.get('error')}")

        # =========================================================
        # PLAYLIST DOWNLOAD WORKFLOW
        # =========================================================
        else:
            st.markdown("### 📁 Playlist Organization")
            safe_folder_name = core.sanitize_filename(info.get("title", "Playlist"))
            dest_folder = os.path.join(core.DEFAULT_DOWNLOAD_DIR, safe_folder_name)
            
            st.markdown(f"""
            <div class="phone-box">
                📁 <b>Dedicated Playlist Folder:</b> <code>downloads/{safe_folder_name}/</code><br>
                ✨ <i>All songs will be grouped cleanly inside this playlist folder with ordered track numbering (01, 02...) so your playlist order is preserved!</i>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### Choose Download Mode")
            download_mode = st.radio(
                "Mode",
                options=["Download ALL songs at once (Full Playlist)", "Choose specific songs to download"],
                index=0,
                label_visibility="collapsed"
            )

            tracks = info.get("tracks", [])
            selected_indices = [t["index"] for t in tracks]

            if download_mode == "Choose specific songs to download":
                st.markdown(f"Select songs from **{len(tracks)}** total tracks:")
                
                sel_all_c1, sel_all_c2 = st.columns([1, 1])
                with sel_all_c1:
                    select_all = st.checkbox("Select All Songs", value=True)
                
                with st.expander("📋 View & Select Tracks", expanded=True):
                    chosen = []
                    for t in tracks:
                        checked = st.checkbox(
                            f"#{t['index']:02d} — {t['title']} ({t['duration']})",
                            value=select_all,
                            key=f"track_{t['index']}"
                        )
                        if checked:
                            chosen.append(t["index"])
                    selected_indices = chosen

            count_to_dl = len(selected_indices)

            # Prefix track number option
            add_prefix = st.checkbox(
                "Prefix track numbers (01, 02...) to preserve playlist sequence",
                value=True,
                help="Recommended so songs play in the original playlist order in music apps and car stereos."
            )

            # Playlist download trigger
            dl_playlist_btn = st.button(
                f"🚀 Download Playlist Now ({count_to_dl} MP3s)",
                type="primary",
                disabled=(count_to_dl == 0),
                use_container_width=True
            )

            if dl_playlist_btn:
                prog_overall = st.progress(0.0)
                status_header = st.empty()
                sub_status = st.empty()

                def playlist_cb(d):
                    idx = d.get("current_index", 1)
                    total = d.get("total_count", 1)
                    title = d.get("track_title", "")
                    pct = min(max(d.get("percent", 0.0) / 100.0, 0.0), 1.0)
                    status = d.get("status", "")
                    prog_overall.progress(pct)
                    status_header.markdown(f"📥 Processing track **{idx} of {total}**: *{title}*")
                    if status == "downloading":
                        sub_status.caption(f"Speed: {d.get('speed_str', '')} | ETA: {d.get('eta_str', '')}")
                    elif status == "converting":
                        sub_status.caption("🔄 Converting to MP3 and embedding tags...")

                with st.spinner(f"Downloading {count_to_dl} songs into dedicated folder..."):
                    res = core.download_playlist(
                        playlist_info=info,
                        selected_indices=selected_indices,
                        output_dir=core.DEFAULT_DOWNLOAD_DIR,
                        subfolder_per_playlist=True,
                        add_track_numbers=add_prefix,
                        bitrate=bitrate,
                        embed_thumbnail=embed_art,
                        overall_progress_callback=playlist_cb,
                    )

                prog_overall.progress(1.0)
                status_header.empty()
                sub_status.empty()

                if res.get("success"):
                    st.success(f"🎉 Successfully downloaded **{res['total_succeeded']}** tracks to: `{res['target_dir']}`")
                    
                    # Actions
                    pl_act_col1, pl_act_col2 = st.columns(2)
                    with pl_act_col1:
                        if st.button("📂 Open Playlist Folder in Finder", use_container_width=True):
                            core.reveal_in_finder(res["target_dir"])
                            st.toast("Opened playlist folder in Finder!")
                    
                    with pl_act_col2:
                        # ZIP download for phone or browser
                        downloaded_file_paths = [t["filepath"] for t in res.get("downloaded_tracks", []) if t.get("filepath")]
                        if downloaded_file_paths:
                            zip_path = core.create_zip_archive(downloaded_file_paths, f"{safe_folder_name}.zip")
                            if os.path.exists(zip_path):
                                with open(zip_path, "rb") as zf:
                                    zip_bytes = zf.read()
                                st.download_button(
                                    label=f"📦 Download Entire Playlist as ZIP ({core.format_bytes(len(zip_bytes))})",
                                    data=zip_bytes,
                                    file_name=f"{safe_folder_name}.zip",
                                    mime="application/zip",
                                    use_container_width=True,
                                    type="primary"
                                )

                    # List downloaded songs with preview players
                    with st.expander(f"🎶 Downloaded Songs List ({len(res['downloaded_tracks'])} Tracks)", expanded=True):
                        for dt in res.get("downloaded_tracks", []):
                            fpath = dt.get("filepath")
                            if fpath and os.path.exists(fpath):
                                c1, c2 = st.columns([3, 1])
                                with c1:
                                    st.write(f"🎵 **{dt.get('title')}** ({dt.get('filesize_str')})")
                                with c2:
                                    with open(fpath, "rb") as audio_file:
                                        st.download_button(
                                            "📥 Save MP3",
                                            data=audio_file.read(),
                                            file_name=os.path.basename(fpath),
                                            mime="audio/mpeg",
                                            key=f"dl_single_{os.path.basename(fpath)}"
                                        )

                else:
                    st.error("❌ Failed to download tracks. Check connection.")

# TAB 2: LIBRARY
with tab_library:
    st.markdown("### 📚 Your Downloaded MP3 Library")
    
    lib_col1, lib_col2 = st.columns([3, 1])
    with lib_col1:
        st.caption(f"Location: `{core.DEFAULT_DOWNLOAD_DIR}`")
    with lib_col2:
        if st.button("🔄 Refresh Library", use_container_width=True):
            st.rerun()

    all_mp3s = core.list_downloaded_mp3s(core.DEFAULT_DOWNLOAD_DIR)
    
    if not all_mp3s:
        st.info("No MP3 files found yet. Download your first YouTube video or playlist above!")
    else:
        st.markdown(f"Found **{len(all_mp3s)}** MP3 files across your downloads.")
        
        # Group by playlist folder
        folders = {}
        for item in all_mp3s:
            folder = item["rel_folder"] if item["rel_folder"] != "." else "Standalone Downloads"
            folders.setdefault(folder, []).append(item)

        for folder_name, items in folders.items():
            with st.expander(f"📁 {folder_name} ({len(items)} tracks)", expanded=(folder_name != "Standalone Downloads")):
                for it in items:
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(f"**{it['name']}**")
                        st.caption(f"Size: {it['size_str']} | Modified: {it['mtime_str']}")
                    with c2:
                        try:
                            with open(it["path"], "rb") as f:
                                st.download_button(
                                    "📥 Download",
                                    data=f.read(),
                                    file_name=it["name"],
                                    mime="audio/mpeg",
                                    key=f"lib_dl_{it['path']}"
                                )
                        except Exception:
                            pass
                    with c3:
                        if st.button("📂 Reveal", key=f"rev_{it['path']}"):
                            core.reveal_in_finder(it["path"])
                            st.toast("Revealed in Finder!")

# TAB 3: MOBILE & DEPLOY GUIDE
with tab_guide:
    st.markdown("### 📱 Using Charcha MP3 on your Phone")
    st.markdown(f"""
    1. **Connect Phone to Same Wi-Fi Network**: Ensure your iPhone or Android phone is on the same Wi-Fi as your Mac.
    2. **Open Safari or Chrome on your Phone**: Enter the local URL:
       ```
       {phone_url}
       ```
       Or scan the QR code in the sidebar!
    3. **Paste any YouTube Video or Playlist link**.
    4. **Download**:
       - For a single video: Tap **"🚀 Download MP3 Now"** and then **"📥 Save MP3 to Phone"** to save it to your phone's Files / Downloads app!
       - For a playlist: Tap **"🚀 Download Playlist Now"** and then **"📦 Download Entire Playlist as ZIP"** to save all songs at once!
    """)

    st.markdown("---")
    st.markdown("### 🚀 Deployment Options (Access Anywhere Outside Home)")
    st.markdown("""
    If you want access outside your home Wi-Fi (e.g. while travelling or on cellular data):
    
    #### Option A: Free Cloud Deployment (Render / Hugging Face Spaces / Railway)
    1. A `Dockerfile` and `requirements.txt` are included in this project.
    2. Push this repo to your GitHub:
       ```bash
       git init
       git add .
       git commit -m "Charcha MP3"
       git remote add origin <your-repo>
       git push -u origin main
       ```
    3. Connect your GitHub repo to **Render.com** (Web Service -> Docker) or **Hugging Face Spaces** (Docker SDK).
    4. It gives you a public HTTPS URL (e.g., `https://charcha-mp3.onrender.com`) accessible from anywhere!

    #### Option B: Tailscale (Free Private Mesh Network)
    - Install **Tailscale** on your Mac and Phone (completely free).
    - Access using your Mac's Tailscale IP from anywhere on 5G/4G with zero port forwarding!
    """)

    st.markdown("---")
    st.markdown("### 💻 Terminal CLI Usage")
    st.code("""
# Download a single video:
python3 downloader.py "https://youtu.be/ZaQqertwNiw"

# Download an entire playlist into its own folder:
python3 downloader.py "https://youtube.com/playlist?list=PLsJfa_-ihm2UHcz0JkP3nCnlvI4xwJTAx"

# List playlist tracks without downloading:
python3 downloader.py "https://youtube.com/playlist?list=..." --list
    """, language="bash")
