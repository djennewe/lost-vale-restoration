#!/bin/bash
# play.sh — Launch the already-installed Lost Vale build in ScummVM.
#
# This does NOT rebuild or reinstall — it just launches the game with whatever
# was last installed by ./install_lv.sh. Use this for quick repeat testing.
#
# To rebuild + reinstall + launch instead, use:  ./install_lv.sh --run
#
# Usage:
#   ./play.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# The patched ScummVM is REQUIRED (M15). There is no stock-ScummVM path: it
# only ever worked with a --stealth build, and stealth mode is retired
# (DD-006b) because it cannot carry the expansion. Stock ScummVM will not
# detect the full-size LV usecode, so falling back to it would launch plain
# Pagan — or nothing — while looking like it worked.
SCUMMVM="${SCUMMVM:-}"
EXTRA_ARGS=""
if [ -z "$SCUMMVM" ]; then
    LV_SCUMMVM="$SCRIPT_DIR/scummvm-lv/scummvm"
    if [ -x "$LV_SCUMMVM" ]; then
        SCUMMVM="$LV_SCUMMVM"
        echo "Using patched ScummVM: $SCUMMVM"
        if [ -f "$SCRIPT_DIR/scummvm-lv/ultima8.dat" ]; then
            EXTRA_ARGS="--extrapath=$SCRIPT_DIR/scummvm-lv"
        fi
    else
        echo "ERROR: patched ScummVM not found at $LV_SCUMMVM"
        echo "  Build it:  ./build_scummvm.sh"
        echo "  (Stock ScummVM cannot detect the Lost Vale build. Set SCUMMVM=..."
        echo "   only if you have another binary carrying the LV detection entry.)"
        exit 1
    fi
fi

cat <<'TELEPORTS'

ScummVM debugger: Cmd+Opt+D (Mac), then:
    Cheat::toggle
    MainActor::teleport 10 5120  7168  0   — Hoskuld (clan) village
    MainActor::teleport 10 19968 7424  0   — Gunnar (Atli's) village
    MainActor::teleport 10 12800 2560  0   — Lost Vale entry area
    MainActor::teleport 8  20430 3250  0   — Map 8  (Bonecrusher cave — THE LV double doors)
    MainActor::teleport 9  14336 12544 0   — Map 9  (Galjeron's Chamber)
    MainActor::teleport 11 9728  1536  0   — Map 11 (Elemental Dungeon)
    MainActor::teleport 13 4096  11776 0   — Map 13 (Cloud Cliffs base)
    MainActor::teleport 17 5376  11520 0   — Map 17 (Cloud City)
    MainActor::teleport 18 3072  1792  0   — Map 18 (Ancient Temple)
  Type 'exit' to return to the game.

TELEPORTS

exec "$SCUMMVM" --debuglevel=1 $EXTRA_ARGS ultima8
