#!/bin/bash
# tools/playtest-linux/shot.sh <out.png> — capture the private display.
#
# The macOS counterpart has to find the window id, avoid -R because a
# screen-rect grab takes whatever is topmost, then crop 68px of drop shadow
# and halve for Retina. None of that applies here: ScummVM is alone and
# fullscreen on its own Xvfb screen, so the root window IS the game surface
# and image pixels are already the coordinates xdotool wants.
set -euo pipefail
OUT="${1:-shot.png}"
DISP="${LV_DISPLAY:-:77}"

DISPLAY="$DISP" xdpyinfo >/dev/null 2>&1 || { echo "no X display $DISP — session.sh start" >&2; exit 1; }
DISPLAY="$DISP" import -window root "$OUT"
echo "$OUT: $(identify -format '%wx%h' "$OUT")"
