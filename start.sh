#!/usr/bin/env bash
# ----------------------------------------------------
# Charcha MP3 - Web App Launcher
# ----------------------------------------------------

cd "$(dirname "$0")"

echo "🎵 Starting Charcha MP3 Web App..."
echo "📱 Listening on local network for phone access..."

python3 -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
