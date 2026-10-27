#!/bin/bash
# Double-click this file in macOS Finder to immediately start Charcha MP3
cd "$(dirname "$0")"
clear
echo "========================================================"
echo "          🎵 CHARCHA MP3 - STUDIO AUDIO STUDIO          "
echo "========================================================"
echo "Starting local server..."
echo "To open on your phone, connect to Wi-Fi and visit:"
echo "http://$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo '127.0.0.1'):8501"
echo "========================================================"
python3 -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
