#!/bin/bash
# shot.sh <out.png> — capture the ScummVM window and crop away the drop shadow,
# leaving a 1450x873 image whose pixel coordinates ARE window-frame points.
# That is the coordinate space postmouse wants (add the window origin).
#
# Uses -l <window-id>, not -R: a screen-rect capture grabs whatever is topmost
# at those coordinates, which is the wrong window whenever ScummVM is in the
# background — the whole point of this harness.
set -euo pipefail
OUT="${1:-shot.png}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID="${LV_PID:-$(pgrep -f 'scummvm-lv.*/scummvm' | head -1)}"
[ -n "$PID" ] || { echo "no running scummvm-lv" >&2; exit 1; }
# winid, not `orca computer list-windows`: orca reports "No windows found"
# when ScummVM is started from session.sh's pipeline subshell, even though
# the window exists.
WIN=$("$HERE/winid" "$PID" | awk '{print $1}')
[ -n "$WIN" ] || { echo "no scummvm window found" >&2; exit 1; }

screencapture -l "$WIN" -x "$OUT"

# The -l capture pads 68px of shadow on each side at 2x scale.
python3 - "$OUT" <<'PY'
import sys
from PIL import Image
p = sys.argv[1]
im = Image.open(p)
w, h = im.size
im.crop((68, 68, w - 68, h - 68)).resize(((w - 136) // 2, (h - 136) // 2)).save(p)
print(f"{p}: {(w-136)//2}x{(h-136)//2}")
PY
