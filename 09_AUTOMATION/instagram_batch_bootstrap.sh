#!/usr/bin/env bash
# Lanzador de una tanda de reels para la tarea programada.
# Instala yt-dlp/faster-whisper si el VM se ha reiniciado y usa el modelo
# guardado en la carpeta del proyecto.
# Descarga con las cookies de la cuenta secundaria; si el archivo no está,
# avisa y continúa en modo anónimo.
set -euo pipefail

cd "$(dirname "$0")/.."
MODEL="$PWD/09_AUTOMATION/models/faster-whisper-small"
COOKIES="$PWD/www.instagram.com_cookies.txt"

if [ ! -f "$MODEL/model.bin" ]; then
  echo "Falta el modelo en $MODEL"
  exit 2
fi

python3 -c "import faster_whisper" 2>/dev/null || \
  pip install --break-system-packages -q faster-whisper

python3 -m yt_dlp --version >/dev/null 2>&1 || \
  pip install --break-system-packages -q yt-dlp

MIN="${1:-2.2}"
LIM="${2:-15}"
COMMON=(--minutes "$MIN" --limit "$LIM" --model "$MODEL" --sleep 2)

if [ -f "$COOKIES" ]; then
  python3 09_AUTOMATION/instagram_reels_batch.py "${COMMON[@]}" --cookies "$COOKIES"
else
  echo "Aviso: no está $COOKIES; se usará yt-dlp anónimo."
  python3 09_AUTOMATION/instagram_reels_batch.py "${COMMON[@]}"
fi
