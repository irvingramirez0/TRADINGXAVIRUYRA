#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
BASE=/sessions/fervent-clever-dirac/mnt/TRADINGXAVIRUYRA
cd "$BASE/03_FRAMES/videos"
for id in t9rcx-dDGvA 3aG0N7aHu4s NDVbDdE5TW0 SuRgJd8ONIc mBHtx-BfWWg 7HOAf7vHMqU; do
  yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" --merge-output-format mp4 \
    -o "%(upload_date)s_%(id)s_%(title).60s.%(ext)s" \
    "https://www.youtube.com/watch?v=$id" >> "$BASE/09_AUTOMATION/logs/download.log" 2>&1
done
echo "DESCARGA COMPLETA $(date)" >> "$BASE/09_AUTOMATION/logs/download.log"
